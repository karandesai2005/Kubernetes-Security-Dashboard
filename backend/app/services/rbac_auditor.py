"""
Kubernetes RBAC audit log analyser.
Detects overpermissioned roles, wildcard bindings, and privilege escalation patterns.
"""
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rbac import RBACEvent
from app.core.config import settings


RBAC_MOCK_PATTERNS = [
    {"verb": "*", "resource": "*", "reason": "wildcard", "allowed": True, "risk": 15},
    {"verb": "create", "resource": "clusterroles", "reason": "cluster-admin", "allowed": True, "risk": 22},
    {"verb": "bind", "resource": "clusterrolebindings", "reason": "escalation", "allowed": True, "risk": 18},
    {"verb": "get", "resource": "secrets", "reason": "cross-ns", "allowed": True, "risk": 7},
    {"verb": "impersonate", "resource": "users", "reason": "impersonate", "allowed": True, "risk": 20},
    {"verb": "delete", "resource": "pods", "reason": "wildcard-ns", "allowed": True, "risk": 9},
]


class RBACAuditor:
    def __init__(self, session: AsyncSession | None = None):
        self.session = session

    async def analyse(self) -> dict:
        """Stub. In real would tail audit logs or analyze collected events."""
        return {"status": "ok", "findings": 0}

    async def seed_mock_events(self, count: int = 11, session: AsyncSession | None = None) -> list[RBACEvent]:
        sess = session or self.session
        if sess is None:
            return []

        now = datetime.now(timezone.utc)
        events: list[RBACEvent] = []
        subjects = [
            "system:serviceaccount:production:ci-deployer",
            "developer-jane",
            "system:serviceaccount:kube-system:default",
            "payments-sa",
            "alice@company.com",
        ]
        namespaces = ["production", "payments", "default", "kube-system"]

        for i in range(count):
            pat = random.choice(RBAC_MOCK_PATTERNS)
            subj = random.choice(subjects)
            ns = random.choice(namespaces) if pat["reason"] != "cluster-admin" else None
            delta = timedelta(minutes=random.randint(15, 1440))
            ts = now - delta

            ev = RBACEvent(
                subject=subj,
                verb=pat["verb"],
                resource=pat["resource"],
                resource_name="*" if pat["resource"] == "*" else f"{pat['resource']}-role",
                namespace=ns,
                allowed=pat["allowed"],
                reason=pat["reason"],
                message=f"Subject {subj} performed {pat['verb']} on {pat['resource']} ({pat['reason']})",
                timestamp=ts,
                risk_score=float(pat["risk"]),
            )
            sess.add(ev)
            events.append(ev)

        await sess.commit()
        for e in events:
            await sess.refresh(e)
        return events

    async def get_recent(self, limit: int = 50, session: AsyncSession | None = None) -> list[RBACEvent]:
        sess = session or self.session
        if sess is None:
            return []
        res = await sess.execute(
            select(RBACEvent).order_by(RBACEvent.timestamp.desc()).limit(limit)
        )
        return list(res.scalars().all())
