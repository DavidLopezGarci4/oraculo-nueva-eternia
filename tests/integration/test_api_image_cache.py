import pytest
from unittest.mock import patch
from src.interfaces.api.routers.vault import _image_download_status, _image_download_lock

async def mock_download_no_clear():
    global _image_download_status
    with _image_download_lock:
        _image_download_status["active"] = True
        _image_download_status["total"] = 10
        _image_download_status["current"] = 5

def test_image_download_endpoints(client):
    # Reset status before testing
    with _image_download_lock:
        _image_download_status["active"] = False
        _image_download_status["total"] = 0
        _image_download_status["current"] = 0
        _image_download_status["errors"] = 0
        _image_download_status["last_error"] = None

    # 1. Check status endpoint (should be inactive)
    resp = client.get("/api/vault/download-images/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["active"] is False

    # Patch the download task to run our mock
    with patch("src.interfaces.api.routers.vault.download_all_images_task", mock_download_no_clear):
        # 2. Trigger download
        resp = client.post("/api/vault/download-images")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("started", "running")

        # 3. Check status (should be active now because mock leaves active = True)
        resp = client.get("/api/vault/download-images/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["active"] is True
        assert data["total"] == 10
        assert data["current"] == 5

        # 4. Try triggering again (should say already running)
        resp = client.post("/api/vault/download-images")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "running"

        # 5. Cancel download
        resp = client.post("/api/vault/download-images/cancel")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "cancelled"

        # 6. Check status again (should be cancelled/inactive)
        resp = client.get("/api/vault/download-images/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["active"] is False

        # 7. Try cancelling again (should say inactive)
        resp = client.post("/api/vault/download-images/cancel")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "inactive"
