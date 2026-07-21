"""
Smoke tests for the response_model contracts added in Fase AAA-2.2.

Each endpoint here previously returned an ad-hoc dict/list with no declared
schema. These tests exercise the real handler and confirm FastAPI's
response_model validation doesn't reject the actual output — i.e. the
Pydantic schema genuinely matches what the handler returns, not just what we
assumed it did. They don't assume an empty DB: the test suite is a shared
session-scoped database, and other test modules insert real rows — if a
schema didn't match that real data, FastAPI would return 500
(ResponseValidationError) instead of 200 here.
"""
from tests.conftest import API_KEY


def test_dashboard_hall_of_fame_matches_schema(client, authorized_device_headers):
    resp = client.get("/api/dashboard/hall-of-fame", headers=authorized_device_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert set(data.keys()) == {"origins", "vintage"}
    for group in (data["origins"], data["vintage"]):
        assert set(group.keys()) == {"top_value", "top_roi"}
        assert isinstance(group["top_value"], list)


def test_dashboard_top_deals_matches_schema(client, authorized_device_headers):
    resp = client.get("/api/dashboard/top-deals", headers=authorized_device_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_dashboard_match_stats_matches_schema(client, authorized_device_headers):
    # No se asume lista vacia: otros tests de la suite (p.ej.
    # test_api_purgatory_bulk.py) insertan OfferModel en la misma BD
    # compartida de sesion. Si el schema no encajase con datos reales,
    # FastAPI devolveria 500 (ResponseValidationError) en vez de 200 aqui.
    resp = client.get("/api/dashboard/match-stats", headers=authorized_device_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    for row in resp.json():
        assert set(row.keys()) == {"shop", "count"}


def test_dashboard_history_matches_schema(client, authorized_device_headers):
    resp = client.get("/api/dashboard/history", headers=authorized_device_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    for row in resp.json():
        assert set(row.keys()) == {"id", "product_name", "shop_name", "price", "action_type", "timestamp", "offer_url"}


def test_dashboard_revert_matches_schema(client):
    resp = client.post(
        "/api/dashboard/revert",
        json={"history_id": 999999},
        headers={"X-API-Key": API_KEY},
    )
    # No existe ese history_id -> 404 antes de construir la respuesta;
    # solo confirma que el guard (verify_api_key) deja pasar y el 404 no
    # rompe la validacion de response_model (los errores no pasan por ahi).
    assert resp.status_code == 404


def test_radar_p2p_opportunities_matches_schema(client, bearer):
    resp = client.get("/api/radar/p2p-opportunities", headers=bearer)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
