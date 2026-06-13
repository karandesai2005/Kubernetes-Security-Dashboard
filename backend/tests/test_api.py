"""API smoke tests."""
import pytest

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# TODO: add tests for /threats, /vulns, /rbac, /risk-score
