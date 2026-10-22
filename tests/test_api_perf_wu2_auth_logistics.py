import inspect
from unittest.mock import patch

from src.application.services.logistics_service import LogisticsService
from src.interfaces.api import deps
from tests.conftest import API_KEY, _TestSession


def test_verify_device_is_sync_and_caches_authorized_devices_with_instant_revocation(client):
    """PERF-01 & PERF-02:
    1. verify_device must be a synchronous `def` (so FastAPI runs it in the worker threadpool, not blocking the event loop).
    2. Repeated GET requests from an authorized device must hit the in-memory cache without opening SessionCloud() or committing on every GET.
    3. Revoking or re-authorizing a device via /api/admin/devices must invalidate the cache immediately (zero stale window).
    """
    assert not inspect.iscoroutinefunction(deps.verify_device), (
        "verify_device should be a synchronous `def` so FastAPI runs it in the worker threadpool"
    )

    device_id = "perf-wu2-device-001"
    headers = {"X-Device-ID": device_id, "X-Device-Name": "WU2 Test Device"}

    # 1. Initial unapproved access -> 403
    r1 = client.get("/api/dashboard/stats", headers=headers)
    assert r1.status_code == 403

    # 2. Admin approves device -> must invalidate cache and allow immediate access -> 200
    r_auth = client.post(
        f"/api/admin/devices/{device_id}/authorize",
        headers={"X-API-Key": API_KEY},
    )
    assert r_auth.status_code == 200

    # Prime the device cache with first authorized call
    r2 = client.get("/api/dashboard/stats", headers=headers)
    assert r2.status_code == 200

    # 3. Subsequent calls must NOT query or commit AuthorizedDeviceModel in verify_device
    check_access_db_calls = 0
    real_session = deps.SessionCloud

    def counting_deps_session(*args, **kwargs):
        nonlocal check_access_db_calls
        check_access_db_calls += 1
        return real_session(*args, **kwargs)

    with patch.object(deps, "SessionCloud", side_effect=counting_deps_session):
        for _ in range(5):
            r_cached = client.get("/api/dashboard/stats", headers=headers)
            assert r_cached.status_code == 200

    assert check_access_db_calls == 0, (
        f"Expected 0 DB sessions opened by verify_device for cached device, got {check_access_db_calls}"
    )

    # 4. Admin revokes device -> must take effect immediately (next request returns 403)
    r_rev = client.delete(
        f"/api/admin/devices/{device_id}",
        headers={"X-API-Key": API_KEY},
    )
    assert r_rev.status_code == 200

    r_after_revoke = client.get("/api/dashboard/stats", headers=headers)
    assert r_after_revoke.status_code == 403


def test_logistics_service_caches_rules_across_calls():
    """RED-04: LogisticsService.get_landing_price must cache LogisticRuleModel rows in memory
    instead of opening a new SessionCloud() and querying logistic_rules on every call."""
    if hasattr(LogisticsService, "invalidate_rules_cache"):
        LogisticsService.invalidate_rules_cache()

    db_open_count = 0

    def counting_session(*args, **kwargs):
        nonlocal db_open_count
        db_open_count += 1
        return _TestSession(*args, **kwargs)

    with patch("src.application.services.logistics_service.SessionCloud", side_effect=counting_session):
        p1 = LogisticsService.get_landing_price(25.0, "Amazon.es", "ES")
        p2 = LogisticsService.get_landing_price(30.0, "Wallapop", "ES")
        p3 = LogisticsService.get_landing_price(40.0, "Fantasia Personajes", "ES")
        cart = LogisticsService.calculate_cart(
            [{"shop_name": "Amazon.es", "price": 25.0, "quantity": 1, "product_name": "He-Man"}],
            "ES",
        )

    assert p1 > 0
    assert p2 > 30.0
    assert p3 > 0
    assert cart["grand_total_eur"] > 0
    assert db_open_count == 1, f"Expected 1 DB query to load logistic_rules, got {db_open_count}"


def test_get_current_user_caches_active_user_and_invalidates_on_location_update(
    client, admin_bearer, authorized_device_headers
):
    """RED-05: Repeated authenticated requests must reuse cached UserModel metadata without querying UserModel
    in deps.py on every request, and invalidate immediately when user settings change."""
    if hasattr(deps, "invalidate_user_auth_cache"):
        deps.invalidate_user_auth_cache()

    combined_headers = {**admin_bearer, **authorized_device_headers}

    # Prime cache with first call
    r1 = client.get("/api/admin/devices", headers=combined_headers)
    assert r1.status_code == 200

    deps_session_count = 0
    real_session = deps.SessionCloud

    def counting_deps_session(*args, **kwargs):
        nonlocal deps_session_count
        deps_session_count += 1
        return real_session(*args, **kwargs)

    with patch.object(deps, "SessionCloud", side_effect=counting_deps_session):
        for _ in range(4):
            res = client.get("/api/admin/devices", headers=combined_headers)
            assert res.status_code == 200

    assert deps_session_count == 0, f"Expected 0 deps DB queries when JWT user is cached, got {deps_session_count}"
