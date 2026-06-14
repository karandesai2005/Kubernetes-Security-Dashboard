"""RBAC audit event model."""
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class RBACEvent(Base):
    __tablename__ = "rbac_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject: Mapped[str] = mapped_column(String(128), nullable=False, index=True)  # user, serviceaccount
    verb: Mapped[str] = mapped_column(String(32), nullable=False)
    resource: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    namespace: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    allowed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(64), nullable=True)  # e.g. "wildcard", "cluster-admin", "escalation"
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    risk_score: Mapped[float] = mapped_column(default=0.0)
