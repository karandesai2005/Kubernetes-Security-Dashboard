"""
Seed the local database with mock Falco events, Trivy findings,
and RBAC anomalies for UI development without a live cluster.

Usage: python scripts/seed-mock-data.py
"""
import asyncio

MOCK_FALCO_EVENTS = [
    # TODO: add realistic Falco alert payloads
]

MOCK_TRIVY_FINDINGS = [
    # TODO: add CVE samples
]

async def seed():
    print("[seed] TODO: connect to DB and insert mock data")

if __name__ == "__main__":
    asyncio.run(seed())
