"""
Tests for endpoint-level permission enforcement.
Validates that API key and device-ID guards reject unauthenticated requests.
"""
from tests.conftest import API_KEY, ADMIN_HEADERS, DEVICE_HEADERS


# ─── Admin endpoints require X-API-Key ───────────────────────────────────────

def test_admin_users_rejects_no_key(client):
    resp = client.get("/api/admin/users")
    assert resp.status_code == 403


def test_admin_users_accepts_api_key(client):
    resp = client.get("/api/admin/users", headers={"X-API-Key": API_KEY})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_admin_create_user_rejects_no_key(client):
    resp = client.post("/api/admin/users/create", json={
        "username": "hacker", "email": "hacker@evil.com", "password": "pw",
    })
    assert resp.status_code == 403


def test_admin_create_user_success(client):
    resp = client.post("/api/admin/users/create", headers={"X-API-Key": API_KEY}, json={
        "username": "admin_created",
        "email": "admin_created@test.com",
        "password": "secure-pass",
        "role": "viewer",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_purgatory_rejects_no_key(client):
    resp = client.get("/api/purgatory")
    assert resp.status_code == 403


def test_purgatory_accepts_api_key(client):
    resp = client.get("/api/purgatory", headers={"X-API-Key": API_KEY})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ─── Public endpoints (no auth) ──────────────────────────────────────────────

def test_products_public(client):
    resp = client.get("/api/products")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_products_search_public(client):
    resp = client.get("/api/products/search", params={"q": "skeletor"})
    assert resp.status_code == 200


# ─── Device-auth endpoints ────────────────────────────────────────────────────

def test_dashboard_stats_rejects_no_device(client):
    resp = client.get("/api/dashboard/stats")
    assert resp.status_code == 403


def test_dashboard_stats_accepts_approved_device(client, authorized_device_headers):
    """A device that went through the real approval flow can access device-gated endpoints."""
    resp = client.get("/api/dashboard/stats", headers=authorized_device_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_products" in data
    assert "financial" in data


def test_dashboard_stats_rejects_pending_device(client):
    """A brand-new, unapproved device must be rejected — API key no longer bypasses this (Fase AAA-1)."""
    resp = client.get("/api/dashboard/stats", headers=DEVICE_HEADERS)
    assert resp.status_code == 403


def test_collection_rejects_unauthenticated(client):
    """Fase AAA-1.2: /api/collection ya no es de lectura anónima (era un IDOR)."""
    resp = client.get("/api/collection", params={"user_id": 999})
    assert resp.status_code == 401


def test_collection_non_admin_cannot_read_other_users(client, bearer, test_user):
    """
    Un viewer autenticado que pide el user_id de OTRA persona debe quedar
    forzado a su propio id (nunca leer la colección ajena) — cierra el IDOR
    original donde cualquiera podía leer cualquier user_id.
    """
    resp = client.get("/api/collection", params={"user_id": 999}, headers=bearer)
    assert resp.status_code == 200
    # Se ignora el user_id=999 solicitado; se sirve la colección del propio
    # usuario autenticado (vacía en este test), nunca la de otro.
    assert resp.json() == []
