"""
API route definitions.
TODO: implement endpoint handlers.
"""
from fastapi import APIRouter

router = APIRouter()

# GET /threats      — paginated Falco + GuardDuty events
# GET /vulns        — Trivy scan results per image/namespace
# GET /rbac         — RBAC audit log summary
# GET /risk-score   — computed cluster risk score
# POST /scan        — trigger on-demand Trivy scan
