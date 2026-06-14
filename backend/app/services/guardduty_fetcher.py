"""
AWS GuardDuty findings fetcher.
Pulls EKS Protection findings and maps them to ThreatEvents.
"""
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.threat import ThreatEvent
from app.core.config import settings


GUARDDUTY_MOCK = [
    {"title": "CryptoCurrency:EC2/BitcoinTool.B!DNS", "sev": "high"},
    {"title": "Backdoor:EC2/CobaltStrike.C", "sev": "critical"},
    {"title": "Discovery:Kubernetes/MaliciousIPCaller.Custom", "sev": "high"},
    {"title": "Execution:Container/ReverseShell", "sev": "critical"},
    {"title": "Persistence:Container/ImageWithWritableFileSystem", "sev": "medium"},
]


class GuardDutyFetcher:
    def __init__(self, session: AsyncSession | None = None):
        self.session = session

    async def fetch_findings(self) -> list[dict[str, Any]]:
        if not settings.enable_guardduty:
            return []
        # Real impl would use boto3 here.
        return []

    async def seed_mock_findings(self, count: int = 6, session: AsyncSession | None = None) -> list[ThreatEvent]:
        sess = session or self.session
        if sess is None:
            return []

        now = datetime.now(timezone.utc)
        events: list[ThreatEvent] = []
        namespaces = ["production", "staging"]

        for i in range(count):
            tpl = random.choice(GUARDDUTY_MOCK)
            sev = tpl["sev"]
            ns = random.choice(namespaces)
            delta = timedelta(minutes=random.randint(30, 720))
            ts = now - delta

            sev_map = {"critical": 22, "high": 13, "medium": 6}
            risk = float(sev_map.get(sev, 3))

            ev = ThreatEvent(
                source="guardduty",
                severity=sev,
                rule=tpl["title"],
                namespace=ns,
                pod=None,
                container=None,
                message=f"AWS GuardDuty: {tpl['title']} detected on EKS cluster",
                timestamp=ts,
                raw_payload={"mock": True, "finding": tpl},
                risk_score=risk,
            )
            sess.add(ev)
            events.append(ev)

        await sess.commit()
        for e in events:
            await sess.refresh(e)
        return events

    async def get_recent(self, limit: int = 30, session: AsyncSession | None = None) -> list[ThreatEvent]:
        sess = session or self.session
        if sess is None:
            return []
        res = await sess.execute(
            select(ThreatEvent)
            .where(ThreatEvent.source == "guardduty")
            .order_by(ThreatEvent.timestamp.desc())
            .limit(limit)
        )
        return list(res.scalars().all())
