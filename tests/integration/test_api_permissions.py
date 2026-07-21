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


# ─── Fase AAA-2.1: cierre de IDOR en /api/users/* ─────────────────────────────

def test_public_showcase_rejects_unauthenticated(client):
    """Antes de la Fase 2.1, esto activaba el escaparate público de CUALQUIER
    usuario sin ninguna autenticación — el hallazgo más grave de esta ronda."""
    resp = client.post("/api/users/999999/public-showcase", params={"is_public": True})
    assert resp.status_code == 401


def test_public_showcase_non_admin_cannot_target_other_user(client, authorized_device_headers):
    """Un viewer no puede activar el escaparate público de OTRO usuario (una
    víctima registrada aparte); la escritura queda forzada a su propia cuenta,
    y la víctima permanece intacta.

    Usa cuentas de atacante/víctima creadas localmente (no los fixtures
    session-scoped `bearer`/`test_user`) para no contaminar su estado y
    afectar a otros tests que dependen de su showcase por defecto (privado).
    """
    attacker = {"username": "showcase_attacker", "email": "attacker@test.com", "password": "attacker-pass-000"}
    victim = {"username": "showcase_victim", "email": "victim@test.com", "password": "victim-pass-000"}
    for account in (attacker, victim):
        reg = client.post("/api/auth/register", json=account)
        assert reg.status_code == 200, reg.text

    attacker_login = client.post("/api/auth/login", json={"email": attacker["email"], "password": attacker["password"]})
    attacker_bearer = {"Authorization": f"Bearer {attacker_login.json()['access_token']}"}

    victim_login = client.post("/api/auth/login", json={"email": victim["email"], "password": victim["password"]})
    victim_id = victim_login.json()["user"]["id"]
    victim_bearer = {"Authorization": f"Bearer {victim_login.json()['access_token']}"}

    # El atacante intenta activar el escaparate de la víctima.
    resp = client.post(
        f"/api/users/{victim_id}/public-showcase", params={"is_public": True}, headers=attacker_bearer
    )
    assert resp.status_code == 200  # queda silenciosamente redirigido a su propia cuenta (la del atacante)

    # Confirma, como la propia víctima, que su escaparate NO fue afectado.
    check = client.get(f"/api/users/{victim_id}", headers={**authorized_device_headers, **victim_bearer})
    assert check.status_code == 200
    assert check.json()["is_public_showcase"] is False


def test_user_settings_non_admin_scoped_to_self(client, bearer, test_user, authorized_device_headers):
    """GET /api/users/{id} con id ajeno debe devolver los datos propios, no los del id pedido."""
    headers = {**authorized_device_headers, **bearer}
    resp = client.get("/api/users/999999", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == test_user["email"]
