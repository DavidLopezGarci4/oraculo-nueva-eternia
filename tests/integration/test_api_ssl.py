"""
Integration tests for the Admin SSL endpoints.
"""
from tests.conftest import API_KEY


def test_get_ssl_status_rejects_unauthenticated(client):
    resp = client.get("/api/admin/ssl/status")
    assert resp.status_code == 403


def test_get_ssl_status_success(client):
    resp = client.get("/api/admin/ssl/status", headers={"X-API-Key": API_KEY})
    assert resp.status_code == 200
    data = resp.json()
    assert "domain" in data
    assert "issuer" in data
    assert "status" in data
    assert "days_remaining" in data
    assert "is_valid" in data
    assert "source" in data
    assert data["domain"] == "oraculo-eternia.duckdns.org"


def test_post_ssl_renew_rejects_unauthenticated(client):
    resp = client.post("/api/admin/ssl/renew", json={"force": True})
    assert resp.status_code == 403


def test_post_ssl_renew_success(client):
    resp = client.post(
        "/api/admin/ssl/renew",
        headers={"X-API-Key": API_KEY},
        json={"force": True}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "renovación" in data["message"].lower() or "ssl" in data["message"].lower()
