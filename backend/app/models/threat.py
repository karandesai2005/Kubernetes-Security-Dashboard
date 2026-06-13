"""Threat event model (Falco + GuardDuty)."""
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ThreatEvent(Base):
    __tablename__ = "threat_events"
    # TODO: define columns — source, severity, rule, namespace, pod, timestamp, raw_payload
    pass
