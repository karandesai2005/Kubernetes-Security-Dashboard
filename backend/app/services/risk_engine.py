"""
Risk scoring engine.
Aggregates signals from Falco, Trivy, GuardDuty, and RBAC auditor
into a single cluster posture score (0–100).
"""
from dataclasses import dataclass
from typing import Literal

Severity = Literal["critical", "high", "medium", "low", "info"]

SEVERITY_WEIGHTS: dict[Severity, float] = {
    "critical": 10.0,
    "high": 6.0,
    "medium": 3.0,
    "low": 1.0,
    "info": 0.2,
}

@dataclass
class SignalBreakdown:
    falco: float = 0.0
    trivy: float = 0.0
    guardduty: float = 0.0
    rbac: float = 0.0

class RiskEngine:
    WEIGHTS = {
        "falco": 0.32,
        "trivy": 0.28,
        "guardduty": 0.22,
        "rbac": 0.18,
    }

    MAX_RAW = 100.0  # cap per category raw contribution

    def _severity_score(self, events: list, max_events: int = 25) -> float:
        """Compute a 0-100 category score from list of items that have .severity or ['severity']."""
        if not events:
            return 0.0
        total = 0.0
        for e in events[:max_events]:
            sev = getattr(e, "severity", None) or (e.get("severity") if isinstance(e, dict) else "info")
            sev = (sev or "info").lower()
            w = SEVERITY_WEIGHTS.get(sev, 0.5)
            total += w
        # normalize: 12 criticals ~ 100+
        score = min(total / 1.2, self.MAX_RAW)
        return round(score, 1)

    def _count_risk(self, items: list, weight_per: float, max_score: float = 100.0) -> float:
        if not items:
            return 0.0
        score = min(len(items) * weight_per, max_score)
        return round(score, 1)

    def compute_from_counts(
        self,
        falco_events: list,
        vuln_findings: list,
        guardduty_findings: list,
        rbac_events: list,
    ) -> tuple[float, SignalBreakdown]:
        """Primary entry point. Returns overall 0-100 and per-category breakdown."""
        # Falco: heavy on criticals + volume
        falco_score = self._severity_score(falco_events)

        # Trivy: volume of high/critical vulns + count
        trivy_score = self._severity_score(vuln_findings)

        # GuardDuty similar
        guardduty_score = self._severity_score(guardduty_findings)

        # RBAC: over-privileged bindings are high signal even in low volume
        rbac_score = self._count_risk(rbac_events, weight_per=4.5, max_score=85.0)

        # Weighted sum
        overall = (
            falco_score * self.WEIGHTS["falco"]
            + trivy_score * self.WEIGHTS["trivy"]
            + guardduty_score * self.WEIGHTS["guardduty"]
            + rbac_score * self.WEIGHTS["rbac"]
        )
        overall = max(0.0, min(100.0, round(overall, 1)))

        return overall, SignalBreakdown(
            falco=round(falco_score, 1),
            trivy=round(trivy_score, 1),
            guardduty=round(guardduty_score, 1),
            rbac=round(rbac_score, 1),
        )

    def compute(self, falco_score: float, trivy_score: float, guardduty_score: float, rbac_score: float) -> float:
        """Direct weighted from already-scored buckets (used by tests / direct calls)."""
        overall = (
            falco_score * self.WEIGHTS["falco"]
            + trivy_score * self.WEIGHTS["trivy"]
            + guardduty_score * self.WEIGHTS["guardduty"]
            + rbac_score * self.WEIGHTS["rbac"]
        )
        return max(0.0, min(100.0, round(overall, 1)))
