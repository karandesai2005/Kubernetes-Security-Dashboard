"""
API route definitions.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.core.config import settings
from app.services.falco_processor import FalcoProcessor
from app.services.trivy_scanner import TrivyScanner
from app.services.guardduty_fetcher import GuardDutyFetcher
from app.services.rbac_auditor import RBACAuditor
from app.services.risk_engine import RiskEngine
from app.models.threat import ThreatEvent
from app.models.vulnerability import VulnerabilityFinding
from app.models.rbac import RBACEvent

router = APIRouter(prefix="/api/v1")

# Pydantic response models
class ThreatOut(BaseModel):
    id: int
    source: str
    severity: str
    rule: str
    namespace: str | None
    pod: str | None
    container: str | None
    message: str
    timestamp: datetime
    risk_score: float

class VulnOut(BaseModel):
    id: int
    cve_id: str
    severity: str
    cvss_score: float | None
    image: str
    package: str | None
    installed_version: str | None
    fixed_version: str | None
    namespace: str | None
    resource_kind: str | None
    title: str | None
    discovered_at: datetime
    risk_score: float

class RBACOut(BaseModel):
    id: int
    subject: str
    verb: str
    resource: str
    resource_name: str | None
    namespace: str | None
    allowed: bool
    reason: str | None
    message: str | None
    timestamp: datetime
    risk_score: float

class RiskScoreOut(BaseModel):
    score: float
    breakdown: dict[str, float]
    generated_at: datetime
    counts: dict[str, int]

class SeedResponse(BaseModel):
    seeded: dict[str, int]
    message: str

@router.get("/health")
async def health():
    return {"status": "ok", "mock": settings.enable_mock_data}

@router.get("/threats", response_model=list[ThreatOut])
async def get_threats(
    limit: int = Query(50, ge=1, le=500),
    source: str | None = None,
    severity: str | None = None,
    namespace: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    proc = FalcoProcessor(db)
    # Combine falco + guardduty
    falco = await proc.get_recent(limit=limit * 2, session=db)
    gd = await GuardDutyFetcher(db).get_recent(limit=limit * 2, session=db)

    events: list[ThreatEvent] = []
    events.extend(falco)
    events.extend(gd)

    # filters
    if source:
        events = [e for e in events if e.source == source]
    if severity:
        events = [e for e in events if e.severity.lower() == severity.lower()]
    if namespace:
        events = [e for e in events if (e.namespace or "").lower() == namespace.lower()]

    events.sort(key=lambda e: e.timestamp, reverse=True)
    return [
        ThreatOut(
            id=e.id,
            source=e.source,
            severity=e.severity,
            rule=e.rule,
            namespace=e.namespace,
            pod=e.pod,
            container=e.container,
            message=e.message,
            timestamp=e.timestamp,
            risk_score=e.risk_score,
        )
        for e in events[:limit]
    ]

@router.get("/vulns", response_model=list[VulnOut])
async def get_vulns(
    limit: int = Query(100, ge=1, le=500),
    namespace: str | None = None,
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    scanner = TrivyScanner(db)
    findings = await scanner.get_findings(limit=limit * 2, namespace=namespace, session=db)
    if severity:
        findings = [f for f in findings if f.severity.lower() == severity.lower()]
    findings.sort(key=lambda f: (f.risk_score, f.discovered_at), reverse=True)
    return [
        VulnOut(
            id=f.id,
            cve_id=f.cve_id,
            severity=f.severity,
            cvss_score=f.cvss_score,
            image=f.image,
            package=f.package,
            installed_version=f.installed_version,
            fixed_version=f.fixed_version,
            namespace=f.namespace,
            resource_kind=f.resource_kind,
            title=f.title,
            discovered_at=f.discovered_at,
            risk_score=f.risk_score,
        )
        for f in findings[:limit]
    ]

@router.get("/rbac", response_model=list[RBACOut])
async def get_rbac(
    limit: int = Query(100, ge=1, le=500),
    namespace: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    auditor = RBACAuditor(db)
    events = await auditor.get_recent(limit=limit, session=db)
    if namespace:
        events = [e for e in events if (e.namespace or "").lower() == namespace.lower()]
    return [
        RBACOut(
            id=e.id,
            subject=e.subject,
            verb=e.verb,
            resource=e.resource,
            resource_name=e.resource_name,
            namespace=e.namespace,
            allowed=e.allowed,
            reason=e.reason,
            message=e.message,
            timestamp=e.timestamp,
            risk_score=e.risk_score,
        )
        for e in events[:limit]
    ]

@router.get("/risk-score", response_model=RiskScoreOut)
async def get_risk_score(db: AsyncSession = Depends(get_db)):
    engine = RiskEngine()

    # Load recent signals
    falco = await FalcoProcessor(db).get_recent(limit=200, session=db)
    vulns = await TrivyScanner(db).get_findings(limit=200, session=db)
    gd = await GuardDutyFetcher(db).get_recent(limit=50, session=db)
    rbac = await RBACAuditor(db).get_recent(limit=100, session=db)

    score, breakdown = engine.compute_from_counts(falco, vulns, gd, rbac)

    return RiskScoreOut(
        score=score,
        breakdown=breakdown.__dict__,
        generated_at=datetime.now(timezone.utc),
        counts={
            "falco": len(falco),
            "trivy": len(vulns),
            "guardduty": len(gd),
            "rbac": len(rbac),
        },
    )

@router.post("/seed", response_model=SeedResponse)
async def seed_mock_data(db: AsyncSession = Depends(get_db)):
    """Seed the DB with realistic mock security signals (idempotent-ish for demo)."""
    if not settings.enable_mock_data:
        return SeedResponse(seeded={}, message="Mock data disabled via config")

    falco_p = FalcoProcessor(db)
    trivy = TrivyScanner(db)
    gd = GuardDutyFetcher(db)
    rbac = RBACAuditor(db)

    # Only seed if tables look empty to avoid huge duplication on repeated calls
    existing_threats = (await db.execute(select(ThreatEvent).limit(1))).scalars().first()
    existing_vulns = (await db.execute(select(VulnerabilityFinding).limit(1))).scalars().first()

    seeded: dict[str, int] = {}

    if not existing_threats:
        f = await falco_p.seed_mock_events(22, session=db)
        g = await gd.seed_mock_findings(7, session=db)
        seeded["falco"] = len(f)
        seeded["guardduty"] = len(g)
    else:
        seeded["falco"] = 0
        seeded["guardduty"] = 0

    if not existing_vulns:
        v = await trivy.seed_mock_findings(28, session=db)
        seeded["trivy"] = len(v)
    else:
        seeded["trivy"] = 0

    existing_rbac = (await db.execute(select(RBACEvent).limit(1))).scalars().first()
    if not existing_rbac:
        r = await rbac.seed_mock_events(13, session=db)
        seeded["rbac"] = len(r)
    else:
        seeded["rbac"] = 0

    msg = "Seeded fresh mock data" if any(seeded.values()) else "Mock data already present"
    return SeedResponse(seeded=seeded, message=msg)

@router.post("/scan/trivy")
async def trigger_trivy_scan(namespace: str = "default", db: AsyncSession = Depends(get_db)):
    """Simulate on-demand Trivy scan trigger (real impl would patch CR or call operator)."""
    scanner = TrivyScanner(db)
    # For demo we just add a couple high severity synthetic findings
    if settings.enable_mock_data:
        new_findings = await scanner.seed_mock_findings(3, session=db)
        return {"status": "triggered", "added": len(new_findings), "namespace": namespace}
    return {"status": "skipped", "reason": "live scans require cluster + Trivy Operator"}
