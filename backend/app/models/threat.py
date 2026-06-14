"""Threat event model (Falco + GuardDuty)."""
from datetime import datetime
from typing import Any
from sqlalchemy import String, Integer, JSON, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ThreatEvent(Base):
    __tablename__ = "threat_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # "falco" | "guardduty"
    severity: Mapped[str] = mapped_column(String(16), nullable=False, index=True)  # critical | high | medium | low | info
    rule: Mapped[str] = mapped_column(String(128), nullable=False)
    namespace: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    pod: Mapped[str | None] = mapped_column(String(128), nullable=True)
    container: Mapped[str | None] = mapped_column(String(128), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    risk_score: Mapped[float] = mapped_column(default=0.0)  # contribution to cluster risk (0-100)
