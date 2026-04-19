"""
Tests for the global exception handlers registered in main.py.
Covers validation errors (422) and ensures 403/404 keep working correctly.
"""


def test_validation_error_returns_structured_json(client):
    """POSTing bad types should trigger RequestValidationError → structured 422."""
    resp = client.post("/api/logistics/calculate-cart", json={"items": "not-a-list", "user_id": 1})
    assert resp.status_code == 422
    data = resp.json()
    assert data["status"] == "error"
    assert data["type"] == "validation_error"
    assert isinstance(data["detail"], list)


def test_missing_required_field_returns_422(client):
    resp = client.post("/api/auth/login", json={"email": "x@x.com"})  # missing password
    assert resp.status_code == 422
    data = resp.json()
    assert data["status"] == "error"
    assert data["type"] == "validation_error"


def test_http_403_still_works(client):
    """HTTPException responses must still reach the client correctly."""
    resp = client.get("/api/admin/users")  # no API key
    assert resp.status_code == 403
    assert "detail" in resp.json()


def test_http_404_still_works(client):
    resp = client.get("/api/users/999999", headers={
        "X-Device-ID": "test-device",
        "X-API-Key": "eternia-shield-2026",
    })
    assert resp.status_code == 404
