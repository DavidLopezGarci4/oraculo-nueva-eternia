import os
import tempfile
from unittest.mock import patch

from src.domain.models import ProductModel, UserModel
from tests.conftest import ADMIN_HEADERS, _TestSession


def test_gzip_middleware_compresses_large_json_responses(client):
    """RED-02: Large JSON payloads (>1000 bytes) must be GZip-compressed when client accepts gzip."""
    with _TestSession() as db:
        for idx in range(25):
            db.add(
                ProductModel(
                    name=f"He-Man Origins Variant Test Figure #{idx} With Long Description Padding",
                    category="Action Figures",
                    sub_category="Origins",
                    figure_id=f"MOTU-GZIP-{idx}",
                    is_vintage=False,
                )
            )
        db.commit()

    headers = {**ADMIN_HEADERS, "Accept-Encoding": "gzip"}
    res = client.get("/api/products?is_vintage=false", headers=headers)
    assert res.status_code == 200
    assert res.headers.get("content-encoding") == "gzip"
    data = res.json()
    assert len(data) >= 25


def test_static_image_sets_cache_control_and_caches_user_paths(client, admin_bearer):
    """RED-01: Static image endpoint must include Cache-Control headers, cache UserModel custom paths,
    and invalidate immediately when update_user_image_paths is called."""
    with tempfile.TemporaryDirectory() as custom_dir_1, tempfile.TemporaryDirectory() as custom_dir_2:
        img_1 = os.path.join(custom_dir_1, "777.webp")
        img_2 = os.path.join(custom_dir_2, "777.webp")
        with open(img_1, "wb") as f:
            f.write(b"RIFF\x10\x00\x00\x00WEBPVP8_CUSTOM_1")
        with open(img_2, "wb") as f:
            f.write(b"RIFF\x10\x00\x00\x00WEBPVP8_CUSTOM_2")

        with _TestSession() as db:
            user = db.query(UserModel).filter(UserModel.email == "admin@test.com").first()
            assert user is not None
            uid = user.id
            user.pc_image_path = custom_dir_1
            db.commit()

        import src.interfaces.api.main as main_mod

        if hasattr(main_mod, "invalidate_user_image_paths_cache"):
            main_mod.invalidate_user_image_paths_cache()

        session_open_count = 0

        def counting_session(*args, **kwargs):
            nonlocal session_open_count
            session_open_count += 1
            return _TestSession(*args, **kwargs)

        with patch("src.infrastructure.database_cloud.SessionCloud", side_effect=counting_session), \
             patch.object(main_mod, "SessionCloud", side_effect=counting_session, create=True):
            for _ in range(4):
                resp = client.get(f"/api/static/images/777.webp?source=custom&user_id={uid}")
                assert resp.status_code == 200
                assert resp.content == b"RIFF\x10\x00\x00\x00WEBPVP8_CUSTOM_1"
                assert "max-age=604800" in resp.headers.get("cache-control", "")

            # Only 1 DB session should have been opened across all 4 image requests
            assert session_open_count == 1

            # Updating user image paths via API must invalidate the cache immediately
            upd = client.post(
                f"/api/users/{uid}/image-paths",
                headers=admin_bearer,
                json={"pc_path": custom_dir_2, "mobile_path": None},
            )
            assert upd.status_code == 200

            resp_after = client.get(f"/api/static/images/777.webp?source=custom&user_id={uid}")
            assert resp_after.status_code == 200
            assert resp_after.content == b"RIFF\x10\x00\x00\x00WEBPVP8_CUSTOM_2"
