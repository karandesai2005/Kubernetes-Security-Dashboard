"""
K8s Security Posture Dashboard — API entrypoint.
"""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logging import logger
from app.db import init_db, close_db, get_db_context
from app.services.falco_processor import FalcoProcessor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting K8s Security Dashboard API", extra={"mock": settings.enable_mock_data})
    await init_db(create_tables=True)

    if settings.enable_mock_data:
        # Seed once on cold start if empty
        async with get_db_context() as session:
            proc = FalcoProcessor(session)
            # lightweight check
            from sqlalchemy import select
            from app.models.threat import ThreatEvent
            has_data = (await session.execute(select(ThreatEvent).limit(1))).scalars().first()
            if not has_data:
                await proc.seed_mock_events(12, session=session)
                logger.info("Auto-seeded initial mock Falco data on startup")

    yield
    # Shutdown
    await close_db()
    logger.info("Shutdown complete")

app = FastAPI(
    title="K8s Security Dashboard API",
    description="Aggregates Falco, Trivy, GuardDuty, and RBAC audit signals into unified risk posture.",
    version="0.2.0",
    lifespan=lifespan,
)

# Allow local frontend + common dev origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# --- WebSocket for real-time-ish threat feed (simulated) ---
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for d in dead:
            self.disconnect(d)

manager = ConnectionManager()

@app.websocket("/ws/threats")
async def ws_threats(ws: WebSocket):
    await manager.connect(ws)
    try:
        # Send a welcome + keep pushing occasional mock events when mock mode
        await ws.send_json({"type": "connected", "ts": datetime.now(timezone.utc).isoformat()})
        while True:
            # Client can also just listen; we push a heartbeat every ~25s in mock mode
            await asyncio.sleep(24)
            if settings.enable_mock_data:
                async with get_db_context() as session:
                    proc = FalcoProcessor(session)
                    # Occasionally synthesize a new live event
                    from app.services.falco_processor import FALCO_MOCK_TEMPLATES
                    import random
                    tpl = random.choice(FALCO_MOCK_TEMPLATES)
                    podname = f"pod-{random.randint(100,999)}"
                    if tpl.get("args", 1) == 2:
                        out = tpl["message"] % (random.choice(["live", "app"]), podname)
                    else:
                        out = tpl["message"] % podname
                    raw = {
                        "rule": tpl["rule"],
                        "priority": tpl["severity"],
                        "output": out,
                        "namespace": random.choice(["production", "staging"]),
                    }
                    try:
                        ev = await proc.process_event(raw)
                        await ws.send_json({
                            "type": "threat",
                            "data": {
                                "id": ev.id,
                                "source": ev.source,
                                "severity": ev.severity,
                                "rule": ev.rule,
                                "namespace": ev.namespace,
                                "message": ev.message,
                                "timestamp": ev.timestamp.isoformat(),
                                "risk_score": ev.risk_score,
                            }
                        })
                    except Exception:
                        pass
    except WebSocketDisconnect:
        manager.disconnect(ws)

@app.get("/health")
async def health():
    return {"status": "ok", "mock": settings.enable_mock_data, "version": "0.2.0"}
