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


def test_collection_toggle_and_update_match_schema(client, bearer):
    """toggle_collection y update_collection_item no tenian ninguna cobertura
    previa; verifica CollectionToggleOutput/StatusMessageOutput contra el
    ciclo real: crear (wish) -> actualizar detalles -> quitar."""
    from src.domain.models import ProductModel
    from src.interfaces.api.routers.collection import SessionCloud

    with SessionCloud() as db:
        product = ProductModel(name="Toggle Test Figure", category="MOTU", figure_id="TGL01")
        db.add(product)
        db.commit()
        db.refresh(product)
        product_id = product.id

    add_resp = client.post(
        "/api/collection/toggle",
        json={"product_id": product_id, "user_id": 999, "wish": True},
        headers=bearer,
    )
    assert add_resp.status_code == 200, add_resp.text
    assert add_resp.json()["action"] == "added_wish"
    assert add_resp.json()["product_id"] == product_id

    update_resp = client.patch(
        f"/api/collection/{product_id}",
        json={"user_id": 999, "condition": "Loose", "grading": 8.5, "notes": "test"},
        headers=bearer,
    )
    assert update_resp.status_code == 200, update_resp.text
    assert update_resp.json()["status"] == "success"

    remove_resp = client.post(
        "/api/collection/toggle",
        json={"product_id": product_id, "user_id": 999, "wish": True},
        headers=bearer,
    )
    assert remove_resp.status_code == 200
    assert remove_resp.json()["action"] == "removed"


def test_wallapop_jobs_full_lifecycle_matches_schema(client):
    """create/pending/list de wallapop_jobs.py no tenian NINGUNA cobertura
    previa. Estos 3 endpoints devuelven el ORM WallapopJobModel directamente
    (via WallapopJobOutput con from_attributes=True) - el patron con mas
    riesgo de que un nombre de campo mal escrito pase desapercibido en un
    simple chequeo de import. Verifica el ciclo real: crear -> reclamar -> listar."""
    headers = {"X-API-Key": API_KEY}

    create_resp = client.post("/api/wallapop/jobs", json={"query": "skeletor"}, headers=headers)
    assert create_resp.status_code == 200, create_resp.text
    created = create_resp.json()
    assert created["status"] == "success"
    assert isinstance(created["job_id"], int)

    claim_resp = client.get("/api/wallapop/jobs/pending", params={"worker_id": "test-worker"}, headers=headers)
    assert claim_resp.status_code == 200, claim_resp.text
    claimed = claim_resp.json()
    assert claimed is not None
    assert claimed["id"] == created["job_id"]
    assert claimed["status"] == "running"
    assert claimed["worker_id"] == "test-worker"

    # Sin más jobs pendientes, debe devolver null (no un error de schema con Optional).
    empty_resp = client.get("/api/wallapop/jobs/pending", headers=headers)
    assert empty_resp.status_code == 200
    assert empty_resp.json() is None

    list_resp = client.get("/api/wallapop/jobs", headers=headers)
    assert list_resp.status_code == 200, list_resp.text
    jobs = list_resp.json()
    assert any(j["id"] == created["job_id"] for j in jobs)


def test_logistics_cart_pending_rules_branch_matches_schema(client, bearer):
    """LogisticsService.calculate_cart devuelve MENOS campos (sin
    total_items_qty/fees_eur) cuando la tienda no tiene LogisticRuleModel
    configurado (status == "PENDING_RULES") — esta rama no tenia cobertura
    previa; valida que CartCalculationOutput acepta el shape reducido real."""
    resp = client.post(
        "/api/logistics/calculate-cart",
        json={"items": [{"product_name": "Figura sin regla", "shop_name": "TiendaSinReglas", "price": 25.0, "quantity": 2}]},
        headers=bearer,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["breakdown"]) == 1
    shop = data["breakdown"][0]
    assert shop["status"] == "PENDING_RULES"
    assert shop["total_items_qty"] is None
    assert shop["fees_eur"] is None
    assert shop["total_eur"] == 50.0


def test_logistics_cart_calculated_branch_matches_schema(client, bearer):
    """Con una LogisticRuleModel real, la rama "CALCULATED" rellena TODOS
    los campos (total_items_qty, fees_eur incluidos) — valida el shape
    completo del schema contra datos reales, no solo el camino reducido."""
    from src.domain.models import LogisticRuleModel
    from src.interfaces.api.routers.logistics import SessionCloud

    with SessionCloud() as db:
        db.add(LogisticRuleModel(
            shop_name="TiendaConReglas", country_code="ES",
            base_shipping=5.0, free_shipping_threshold=0.0,
            vat_multiplier=1.21, custom_fees=1.5,
        ))
        db.commit()

    resp = client.post(
        "/api/logistics/calculate-cart",
        json={"items": [{"product_name": "Figura con regla", "shop_name": "TiendaConReglas", "price": 30.0, "quantity": 1}]},
        headers=bearer,
    )
    assert resp.status_code == 200
    shop = resp.json()["breakdown"][0]
    assert shop["status"] == "CALCULATED"
    assert shop["total_items_qty"] == 1
    assert shop["fees_eur"] == 1.5


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
