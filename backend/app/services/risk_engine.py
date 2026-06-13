"""
Risk scoring engine.
Aggregates signals from Falco, Trivy, GuardDuty, and RBAC auditor
into a single cluster posture score (0–100).

TODO: implement weighting logic and normalisation.
"""

class RiskEngine:
    WEIGHTS = {
        "falco": 0.30,
        "trivy": 0.30,
        "guardduty": 0.25,
        "rbac": 0.15,
    }

    def compute(self, falco_score, trivy_score, guardduty_score, rbac_score) -> float:
        raise NotImplementedError
