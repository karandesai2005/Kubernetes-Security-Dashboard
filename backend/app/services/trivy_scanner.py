"""
Trivy Operator integration.
Watches VulnerabilityReport CRDs in the cluster and syncs findings to DB.
"""
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vulnerability import VulnerabilityFinding
from app.core.config import settings


TRIVY_MOCK_CVES = [
    {"cve": "CVE-2024-3094", "sev": "critical", "cvss": 10.0, "pkg": "xz-utils", "title": "xz backdoor in liblzma"},
    {"cve": "CVE-2024-21626", "sev": "critical", "cvss": 9.8, "pkg": "runc", "title": "runc container breakout"},
    {"cve": "CVE-2023-4911", "sev": "high", "cvss": 7.8, "pkg": "glibc", "title": "Looney Tunables"},
    {"cve": "CVE-2023-38545", "sev": "high", "cvss": 7.5, "pkg": "curl", "title": "SOCKS5 heap buffer overflow"},
    {"cve": "CVE-2024-1086", "sev": "high", "cvss": 7.8, "pkg": "kernel", "title": "nf_tables UAF"},
    {"cve": "CVE-2023-36884", "sev": "medium", "cvss": 5.3, "pkg": "busybox", "title": "Multiple busybox vulns"},
    {"cve": "CVE-2023-29469", "sev": "medium", "cvss": 6.5, "pkg": "libwebp", "title": "webp heap buffer overflow"},
    {"cve": "CVE-2024-6387", "sev": "high", "cvss": 8.1, "pkg": "openssh", "title": "regreSSHion"},
]


class TrivyScanner:
    def __init__(self, session: AsyncSession | None = None):
        self.session = session

    async def sync_findings(self, namespace: str = "default") -> int:
        """In production would list CRDs; here just a stub returning count."""
        # Placeholder — real impl would use k8s client + VulnerabilityReport kind
        return 0

    async def seed_mock_findings(self, count: int = 22, session: AsyncSession | None = None) -> list[VulnerabilityFinding]:
        sess = session or self.session
        if sess is None:
            return []

        now = datetime.now(timezone.utc)
        findings: list[VulnerabilityFinding] = []
        images = [
            "registry.internal/api:v2.14.3",
            "docker.io/bitnami/postgresql:16.2.0",
            "gcr.io/distroless/python3.11",
            "quay.io/prometheus/node-exporter:v1.7.0",
            "registry.internal/payments-worker:2024.05",
            "nginx:1.25.4-alpine",
        ]
        namespaces = ["production", "staging", "payments", "default"]

        for i in range(count):
            tpl = random.choice(TRIVY_MOCK_CVES)
            img = random.choice(images)
            ns = random.choice(namespaces)
            delta = timedelta(hours=random.randint(1, 120))
            disc = now - delta

            sev = tpl["sev"]
            sev_risk = {"critical": 14, "high": 8, "medium": 3.5, "low": 1.2}.get(sev, 1.0)

            f = VulnerabilityFinding(
                cve_id=tpl["cve"],
                severity=sev,
                cvss_score=tpl.get("cvss"),
                image=img,
                package=tpl["pkg"],
                installed_version=f"{random.randint(1,4)}.{random.randint(0,20)}.{random.randint(0,9)}",
                fixed_version=f"{random.randint(1,4)}.{random.randint(10,30)}.{random.randint(0,9)}" if random.random() > 0.25 else None,
                namespace=ns,
                resource_kind=random.choice(["Deployment", "StatefulSet", "DaemonSet", "Pod"]),
                title=tpl["title"],
                description=f"Trivy found {tpl['cve']} in {tpl['pkg']}",
                discovered_at=disc,
                risk_score=sev_risk,
            )
            sess.add(f)
            findings.append(f)

        await sess.commit()
        for f in findings:
            await sess.refresh(f)
        return findings

    async def get_findings(self, limit: int = 100, namespace: str | None = None, session: AsyncSession | None = None) -> list[VulnerabilityFinding]:
        sess = session or self.session
        if sess is None:
            return []
        stmt = select(VulnerabilityFinding)
        if namespace:
            stmt = stmt.where(VulnerabilityFinding.namespace == namespace)
        stmt = stmt.order_by(VulnerabilityFinding.discovered_at.desc()).limit(limit)
        res = await sess.execute(stmt)
        return list(res.scalars().all())
