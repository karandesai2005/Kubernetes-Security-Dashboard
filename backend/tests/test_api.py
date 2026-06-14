"""API smoke tests."""
import pytest

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

@pytest.mark.asyncio
async def test_risk_score_endpoint(client):
    r = await client.get("/api/v1/risk-score")
    assert r.status_code in (200, 503)  # may be empty until seed but should not 500

@pytest.mark.asyncio
async def test_threats_endpoint(client):
    r = await client.get("/api/v1/threats?limit=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
