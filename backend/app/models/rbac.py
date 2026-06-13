"""RBAC audit event model."""
from app.models.base import Base

class RBACEvent(Base):
    __tablename__ = "rbac_events"
    # TODO: user, verb, resource, namespace, allowed, timestamp
    pass
