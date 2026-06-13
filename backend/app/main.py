"""
K8s Security Posture Dashboard — API entrypoint.
TODO: wire up routers, middleware, and startup events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="K8s Security Dashboard API",
    description="Aggregates Falco, Trivy, GuardDuty, and RBAC audit signals.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


# TODO: include routers
# from app.api.routes import router
# app.include_router(router, prefix="/api/v1")
