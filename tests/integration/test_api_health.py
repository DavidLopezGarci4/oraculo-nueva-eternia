"""Tests for /api/health — no auth required."""


def test_health_returns_ok(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "oraculo"


def test_health_no_auth_required(client):
    """Health endpoint must be reachable without any headers."""
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_openapi_schema_available(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "paths" in resp.json()
