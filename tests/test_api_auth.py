"""Tests for /api/auth/* — registration, login, JWT tokens."""


def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "username": "newguardian",
        "email": "guardian@test.com",
        "password": "guardian-pass-456",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_register_duplicate_email(client, test_user):
    resp = client.post("/api/auth/register", json={
        "username": "other",
        "email": test_user["email"],
        "password": "x",
    })
    assert resp.status_code == 400


def test_register_duplicate_username(client, test_user):
    resp = client.post("/api/auth/register", json={
        "username": test_user["username"],
        "email": "other@test.com",
        "password": "x",
    })
    assert resp.status_code == 400


def test_login_returns_token(client, test_user):
    resp = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user["email"]


def test_login_wrong_password(client, test_user):
    resp = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": "totally-wrong",
    })
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/api/auth/login", json={
        "email": "nobody@nowhere.com",
        "password": "irrelevant",
    })
    assert resp.status_code == 401


def test_jwt_get_current_user(client, bearer):
    """Token from login must authenticate /api/users/{id} correctly."""
    from tests.conftest import API_KEY, DEVICE_HEADERS
    resp = client.post("/api/auth/login", json={"email": "viewer@test.com", "password": "viewer-pass-123"})
    user_id = resp.json()["user"]["id"]

    # verify_device auto-authorizes when X-API-Key is present
    headers = {**DEVICE_HEADERS, "Authorization": bearer["Authorization"]}
    resp2 = client.get(f"/api/users/{user_id}", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["id"] == user_id
