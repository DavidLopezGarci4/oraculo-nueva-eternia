"""
Test infrastructure for the Oráculo API.

Uses an in-memory SQLite database (StaticPool) so tests are hermetic and fast.
All routers import SessionCloud at module level, so we patch each namespace.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch
from fastapi.testclient import TestClient

# ─── In-memory test database ────────────────────────────────────────────────

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(bind=TEST_ENGINE, autocommit=False, autoflush=False)

# Every router namespace that calls SessionCloud() directly
_SESSION_TARGETS = [
    "src.interfaces.api.routers.admin.SessionCloud",
    "src.interfaces.api.routers.products.SessionCloud",
    "src.interfaces.api.routers.collection.SessionCloud",
    "src.interfaces.api.routers.purgatory.SessionCloud",
    "src.interfaces.api.routers.dashboard.SessionCloud",
    "src.interfaces.api.routers.users.SessionCloud",
    "src.interfaces.api.routers.system.SessionCloud",
    "src.interfaces.api.routers.vault.SessionCloud",
    "src.interfaces.api.routers.logistics.SessionCloud",
    "src.interfaces.api.routers.auth.SessionCloud",
    "src.interfaces.api.routers.showcase.SessionCloud",
    "src.interfaces.api.deps.SessionCloud",
]

# ─── Shared constants ────────────────────────────────────────────────────────

API_KEY = "eternia-shield-2026"  # default dev key from config.py
# Fase AAA-1: X-API-Key es EXCLUSIVAMENTE server-to-server (scrapers/admin panel
# autenticado por JWT). Ya no autoriza dispositivos ni actúa como bypass de login.

ADMIN_HEADERS = {
    "X-API-Key": API_KEY,
    "X-Device-ID": "test-device-admin",
    "X-Device-Name": "Test Runner",
}

# Headers de un dispositivo que TODAVÍA no ha sido aprobado manualmente.
# Úsalo para probar el camino "pendiente de aprobación" (403).
DEVICE_HEADERS = {
    "X-Device-ID": "test-device-user",
    "X-Device-Name": "Test Runner",
}


# ─── Session-scoped fixtures ─────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client():
    """
    FastAPI TestClient backed by an in-memory SQLite database.
    Patches are started before the app is imported so that startup code
    (ensure_scrapers_registered) already uses the test DB.
    """
    from src.domain.models import Base
    Base.metadata.create_all(bind=TEST_ENGINE)

    active = []
    for target in _SESSION_TARGETS:
        p = patch(target, _TestSession)
        p.start()
        active.append(p)

    # Suppress init_cloud_db so it doesn't touch any SQLite file
    p_init = patch("src.infrastructure.database_cloud.init_cloud_db", return_value=None)
    p_init.start()
    active.append(p_init)

    from src.interfaces.api.main import app
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    for p in active:
        p.stop()
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture(scope="session")
def test_user(client):
    """Register a viewer user once and return its credentials."""
    payload = {"username": "testviewer", "email": "viewer@test.com", "password": "viewer-pass-123"}
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 200, resp.text
    return payload


@pytest.fixture(scope="session")
def viewer_token(client, test_user):
    """JWT token for the viewer test user."""
    resp = client.post("/api/auth/login", json={"email": test_user["email"], "password": test_user["password"]})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def bearer(viewer_token):
    """Authorization header with viewer JWT."""
    return {"Authorization": f"Bearer {viewer_token}"}


@pytest.fixture(scope="session")
def admin_user(client):
    """Create an admin-role user via the service-to-service admin endpoint."""
    payload = {"username": "testadmin", "email": "admin@test.com", "password": "admin-pass-789", "role": "admin"}
    resp = client.post("/api/admin/users/create", headers={"X-API-Key": API_KEY}, json=payload)
    assert resp.status_code == 200, resp.text
    return payload


@pytest.fixture(scope="session")
def admin_bearer(client, admin_user):
    """Authorization header with an admin JWT (real login, not the API-key bypass)."""
    resp = client.post("/api/auth/login", json={"email": admin_user["email"], "password": admin_user["password"]})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture(scope="session")
def authorized_device_headers(client):
    """
    Headers for a device that has gone through the REAL approval flow:
    1. First request registers it as pending (is_authorized=False).
    2. An admin (service API key) approves it via /api/admin/devices/{id}/authorize.
    No API key is embedded in the returned headers — device auth alone is enough
    afterwards, matching what a real browser sends post-approval.
    """
    device_id = "test-device-approved"
    headers = {"X-Device-ID": device_id, "X-Device-Name": "Test Runner"}

    # 1. Trigger registration (expected 403 — pending approval)
    client.get("/api/dashboard/stats", headers=headers)

    # 2. Approve it as an admin would (service-to-service API key)
    resp = client.post(
        f"/api/admin/devices/{device_id}/authorize",
        headers={"X-API-Key": API_KEY},
    )
    assert resp.status_code == 200, resp.text

    return headers
