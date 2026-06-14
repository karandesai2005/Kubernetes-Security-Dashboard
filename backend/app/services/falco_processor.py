"""
Falco gRPC / webhook event processor.
Consumes events and persists them as ThreatEvent records.
"""
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.threat import ThreatEvent
from app.core.config import settings


FALCO_MOCK_TEMPLATES = [
    {
        "rule": "Terminal shell in container",
        "message": "A shell was spawned in a container with an attached TTY (user %s in pod %s)",
        "args": 2,
        "severity": "high",
    },
    {
        "rule": "Write to /etc/ in container",
        "message": "Process %s attempted to write to /etc/ in container (pod %s)",
        "args": 2,
        "severity": "critical",
    },
    {
        "rule": "Outbound connection to C2 server",
        "message": "Unexpected outbound connection to known malicious IP from pod %s",
        "args": 1,
        "severity": "critical",
    },
    {
        "rule": "Privileged container launched",
        "message": "Privileged container started in namespace %s (pod %s)",
        "args": 2,
        "severity": "high",
    },
    {
        "rule": "Sensitive file access",
        "message": "Access to sensitive file /root/.kube/config from pod %s",
        "args": 1,
        "severity": "medium",
    },
    {
        "rule": "Namespace pod created with hostNetwork",
        "message": "Pod %s created using hostNetwork in namespace %s",
        "args": 2,
        "severity": "medium",
    },
]


class FalcoProcessor:
    def __init__(self, session: AsyncSession | None = None):
        self.session = session

    async def process_event(self, raw: dict[str, Any]) -> ThreatEvent:
        """Normalize + persist a single Falco-style event."""
        source = "falco"
        severity = (raw.get("priority") or raw.get("severity") or "info").lower()
        rule = raw.get("rule", "Unknown Falco Rule")
        ns = raw.get("namespace") or raw.get("output_fields", {}).get("k8s.ns.name")
        pod = raw.get("pod") or raw.get("output_fields", {}).get("k8s.pod.name")
        container = raw.get("container") or raw.get("output_fields", {}).get("container.name")
        message = raw.get("output", raw.get("message", rule))
        ts_raw = raw.get("time") or raw.get("timestamp")
        try:
            ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00")) if ts_raw else datetime.now(timezone.utc)
        except Exception:
            ts = datetime.now(timezone.utc)

        # simplistic risk contribution
        sev_map = {"critical": 18, "high": 11, "medium": 5, "low": 2, "info": 0.5}
        risk = float(sev_map.get(severity, 1.0))

        event = ThreatEvent(
            source=source,
            severity=severity,
            rule=rule,
            namespace=ns,
            pod=pod,
            container=container,
            message=message,
            timestamp=ts,
            raw_payload=raw,
            risk_score=risk,
        )
        if self.session:
            self.session.add(event)
            await self.session.commit()
            await self.session.refresh(event)
        return event

    async def seed_mock_events(self, count: int = 18, session: AsyncSession | None = None) -> list[ThreatEvent]:
        """Generate realistic mock Falco events (used when ENABLE_MOCK_DATA)."""
        sess = session or self.session
        if sess is None:
            return []

        now = datetime.now(timezone.utc)
        events: list[ThreatEvent] = []
        namespaces = ["production", "staging", "payments", "monitoring", "kube-system"]
        pods = ["api-server", "worker-7f9d", "db-primary", "redis-0", "auth-svc", "frontend-6b8c"]

        for i in range(count):
            tpl = random.choice(FALCO_MOCK_TEMPLATES)
            sev = tpl["severity"]
            ns = random.choice(namespaces)
            pod = random.choice(pods) + f"-{random.randint(10,99)}"
            delta = timedelta(minutes=random.randint(2, 480))
            ts = now - delta

            users = ["root", "app", "nobody"]
            if tpl.get("args", 1) == 2:
                msg = tpl["message"] % (random.choice(users), pod)
            else:
                msg = tpl["message"] % pod

            sev_map = {"critical": 18, "high": 11, "medium": 5, "low": 2, "info": 0.5}
            risk = float(sev_map.get(sev, 1.0))

            ev = ThreatEvent(
                source="falco",
                severity=sev,
                rule=tpl["rule"],
                namespace=ns,
                pod=pod,
                container="app" if "container" in tpl["rule"].lower() else None,
                message=msg,
                timestamp=ts,
                raw_payload={"mock": True, "template": tpl["rule"]},
                risk_score=risk,
            )
            sess.add(ev)
            events.append(ev)

        await sess.commit()
        for e in events:
            await sess.refresh(e)
        return events

    async def get_recent(self, limit: int = 50, session: AsyncSession | None = None) -> list[ThreatEvent]:
        sess = session or self.session
        if sess is None:
            return []
        res = await sess.execute(
            select(ThreatEvent).order_by(ThreatEvent.timestamp.desc()).limit(limit)
        )
        return list(res.scalars().all())
