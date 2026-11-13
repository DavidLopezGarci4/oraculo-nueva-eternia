"""
Contratos HTTP y seguridad del Grimorio MOTU (/api/lore).

Hermético: usa la BD SQLite en memoria de `tests/conftest.py` (sin tocar `oraculo.db`) y
sin ninguna peticion de red (la cosecha de wiki nunca se alcanza en estos casos).
"""
import pytest

from src.domain.models import CharacterLoreModel, ProductLoreModel, ProductModel
from src.application.services.product_lore_seed import ProductLoreSeedService
from tests.conftest import _TestSession


@pytest.fixture
def origins_product(client):
    with _TestSession() as db:
        product = ProductModel(
            name="Sun-Man", category="Action Figures", sub_category="Origins",
            figure_id="LORE-SEC-ORIGINS", is_vintage=False,
        )
        db.add(product)
        db.commit()
        pid = product.id
    yield pid
    with _TestSession() as db:
        db.query(ProductLoreModel).filter(ProductLoreModel.product_id == pid).delete()
        db.query(ProductModel).filter(ProductModel.id == pid).delete()
        db.commit()


@pytest.fixture
def vintage_product(client):
    with _TestSession() as db:
        product = ProductModel(
            name="He-Man Vintage 1982", category="Action Figures", sub_category="Vintage",
            figure_id="LORE-SEC-VINTAGE", is_vintage=True,
        )
        db.add(product)
        db.commit()
        pid = product.id
    yield pid
    with _TestSession() as db:
        db.query(ProductModel).filter(ProductModel.id == pid).delete()
        db.commit()


@pytest.fixture
def admin_headers(authorized_device_headers, admin_bearer):
    return {**authorized_device_headers, **admin_bearer}


@pytest.fixture
def viewer_headers(authorized_device_headers, bearer):
    return {**authorized_device_headers, **bearer}


# ─── Escudo 3OX (verify_device) ───

def test_reads_require_authorized_device(client):
    assert client.get("/api/lore/characters").status_code == 403
    assert client.get("/api/lore/products").status_code == 403


# ─── RBAC: mutaciones solo para administrador ───

def _mutation_calls(pid):
    return [
        ("put", "/api/lore/he_man", {"lore": "x"}),
        ("put", f"/api/lore/product/{pid}", {"lore": "x"}),
        ("post", "/api/lore/harvest", {"character_name": "He-Man"}),
        ("post", f"/api/lore/harvest-product/{pid}", None),
        ("post", "/api/lore/harvest-missing", None),
        ("post", "/api/lore/seed", None),
    ]


def test_mutations_forbidden_for_non_admin(client, viewer_headers, origins_product):
    for method, url, body in _mutation_calls(origins_product):
        resp = getattr(client, method)(url, headers=viewer_headers, json=body) if body is not None \
            else getattr(client, method)(url, headers=viewer_headers)
        assert resp.status_code == 403, f"{method.upper()} {url} -> {resp.status_code}"


def test_mutations_rejected_without_token(client, authorized_device_headers, origins_product):
    for method, url, body in _mutation_calls(origins_product):
        resp = getattr(client, method)(url, headers=authorized_device_headers, json=body) if body is not None \
            else getattr(client, method)(url, headers=authorized_device_headers)
        assert resp.status_code in (401, 403), f"{method.upper()} {url} -> {resp.status_code}"


# ─── GET puro (sin escrituras) ───

def test_get_product_lore_is_pure_read(client, authorized_device_headers, origins_product):
    resp = client.get(f"/api/lore/product/{origins_product}", headers=authorized_device_headers)
    assert resp.status_code == 200
    assert resp.json()["product_id"] == origins_product
    with _TestSession() as db:
        assert db.query(ProductLoreModel).filter(ProductLoreModel.product_id == origins_product).count() == 0


# ─── Exclusion Vintage ───

def test_vintage_products_rejected(client, authorized_device_headers, admin_headers, vintage_product):
    assert client.get(f"/api/lore/product/{vintage_product}", headers=authorized_device_headers).status_code == 400
    resp = client.put(f"/api/lore/product/{vintage_product}", headers=admin_headers, json={"lore": "x"})
    assert resp.status_code == 400


# ─── Escritura de administrador y validacion de entrada ───

def test_admin_put_product_lore_persists_and_marks_customized(client, admin_headers, origins_product):
    resp = client.put(
        f"/api/lore/product/{origins_product}",
        headers=admin_headers,
        json={"lore": "Biografía del Master", "mana_cost": "{1}{R}{R}", "fuerza": 99, "faction": "Gobernantes de Solaria"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["is_customized"] is True and body["mana_cost"] == "{1}{R}{R}"
    assert body["theme_key"] == "castle_grayskull"  # derivado de la facción
    with _TestSession() as db:
        row = db.query(ProductLoreModel).filter(ProductLoreModel.product_id == origins_product).first()
        assert row.is_customized is True and row.fuerza == 99


def test_put_validation_rejects_bad_stats_and_faction(client, admin_headers):
    assert client.put("/api/lore/he_man", headers=admin_headers, json={"fuerza": 150}).status_code == 422
    assert client.put("/api/lore/he_man", headers=admin_headers, json={"fuerza": 0}).status_code == 422
    resp = client.put("/api/lore/he_man", headers=admin_headers, json={"faction": "Facción Inexistente"})
    assert resp.status_code == 422


# ─── Cosecha: 409 sin force sobre personajes verificados (sin red) ───

def test_harvest_verified_character_returns_conflict_without_force(client, admin_headers):
    with _TestSession() as db:
        db.add(CharacterLoreModel(
            slug="conflict_test_char", canonical_name="Conflict Test Char", faction="Guerreros Heroicos",
            theme_key="castle_grayskull", type_line="t", special_move="s", lore="curado", is_verified=True,
            source_url="Curado por Master",
        ))
        db.commit()
    try:
        resp = client.post("/api/lore/harvest", headers=admin_headers, json={"character_name": "Conflict Test Char"})
        assert resp.status_code == 409
    finally:
        with _TestSession() as db:
            db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == "conflict_test_char").delete()
            db.commit()


def test_harvest_name_length_is_validated(client, admin_headers):
    resp = client.post("/api/lore/harvest", headers=admin_headers, json={"character_name": "x" * 121})
    assert resp.status_code == 422


# ─── Listado: el sembrado incremental mantiene visibles las figuras en filtros SQL ───

def test_incremental_seed_keeps_new_origins_visible_to_faction_filter(client, admin_headers, origins_product):
    with _TestSession() as db:
        res = ProductLoreSeedService.seed_missing_origins_products(db)
        assert origins_product in res["created_ids"]
        again = ProductLoreSeedService.seed_missing_origins_products(db)
        assert again["created"] == 0  # idempotente

    resp = client.get("/api/lore/products", headers=admin_headers,
                      params={"faction": "Gobernantes de Solaria", "search": "Sun-Man"})
    assert resp.status_code == 200
    assert origins_product in [i["product_id"] for i in resp.json()["items"]]


def test_products_endpoint_supports_high_limit_figure_id_search_customized_and_sub_categories(
    client, admin_headers, origins_product
):
    with _TestSession() as db:
        ProductLoreSeedService.seed_missing_origins_products(db)

    # Limite > 200 (hasta 500) + exposición de figure_id y sub_categories
    resp = client.get("/api/lore/products", headers=admin_headers, params={"limit": 400})
    assert resp.status_code == 200
    body = resp.json()
    assert "Origins" in body["sub_categories"]
    matched = [i for i in body["items"] if i["product_id"] == origins_product]
    assert len(matched) == 1
    assert matched[0]["figure_id"] == "LORE-SEC-ORIGINS"
    assert matched[0]["is_customized"] is False

    # Búsqueda por figure_id exacto y por #ID interno
    by_fid = client.get("/api/lore/products", headers=admin_headers, params={"search": "LORE-SEC-ORIGINS"})
    assert by_fid.status_code == 200
    assert [i["product_id"] for i in by_fid.json()["items"]] == [origins_product]

    by_pid = client.get("/api/lore/products", headers=admin_headers, params={"search": f"#{origins_product}"})
    assert by_pid.status_code == 200
    assert [i["product_id"] for i in by_pid.json()["items"]] == [origins_product]

    # Cambio rápido de bando mediante PUT parcial recalcula theme_key y marca is_customized=True
    put_resp = client.put(
        f"/api/lore/product/{origins_product}",
        headers=admin_headers,
        json={"faction": "La Horda del Terror"},
    )
    assert put_resp.status_code == 200, put_resp.text
    put_body = put_resp.json()
    assert put_body["faction"] == "La Horda del Terror"
    assert put_body["theme_key"] == "evil_horde"
    assert put_body["is_customized"] is True
    assert put_body["figure_id"] == "LORE-SEC-ORIGINS"

    # Filtro editorial customized=CUSTOMIZED | DEFAULT
    cust_resp = client.get(
        "/api/lore/products",
        headers=admin_headers,
        params={"search": "LORE-SEC-ORIGINS", "customized": "CUSTOMIZED"},
    )
    assert cust_resp.status_code == 200
    assert [i["product_id"] for i in cust_resp.json()["items"]] == [origins_product]

    def_resp = client.get(
        "/api/lore/products",
        headers=admin_headers,
        params={"search": "LORE-SEC-ORIGINS", "customized": "DEFAULT"},
    )
    assert def_resp.status_code == 200
    assert def_resp.json()["items"] == []
