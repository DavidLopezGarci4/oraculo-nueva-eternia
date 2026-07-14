"""
Tests unitarios (offline) para el núcleo firmado de Wallapop (Fase 1 del plan
docs/technical/PLAN_WALLAPOP_NEXUS_LOCAL.md).

No hacen red: validan la firma HMAC, el override de secreto por entorno y el
parseo de la estructura JSON real de /api/v3/search (capturada en incursión real).
"""
import os

import pytest

from src.infrastructure.scrapers.wallapop_signer import WallapopSigner
from src.infrastructure.scrapers.wallapop_scraper import WallapopScraper


def test_signature_is_deterministic_for_fixed_timestamp():
    sig1, ts1 = WallapopSigner.generate_signature("GET", "/api/v3/search?keywords=motu", timestamp=1700000000000)
    sig2, ts2 = WallapopSigner.generate_signature("GET", "/api/v3/search?keywords=motu", timestamp=1700000000000)
    assert sig1 == sig2
    assert ts1 == ts2 == 1700000000000


def test_signature_changes_with_path():
    sig_a, _ = WallapopSigner.generate_signature("GET", "/api/v3/search?keywords=motu", timestamp=1700000000000)
    sig_b, _ = WallapopSigner.generate_signature("GET", "/api/v3/search?keywords=other", timestamp=1700000000000)
    assert sig_a != sig_b


def test_signature_respects_env_secret_override(monkeypatch):
    monkeypatch.setenv("WALLAPOP_SIGN_SECRET", "un-secreto-de-prueba-completamente-distinto")
    sig_override, _ = WallapopSigner.generate_signature("GET", "/api/v3/search?keywords=motu", timestamp=1700000000000)
    monkeypatch.delenv("WALLAPOP_SIGN_SECRET", raising=False)
    sig_default, _ = WallapopSigner.generate_signature("GET", "/api/v3/search?keywords=motu", timestamp=1700000000000)
    assert sig_override != sig_default


def test_signature_explicit_secret_still_wins_over_env(monkeypatch):
    monkeypatch.setenv("WALLAPOP_SIGN_SECRET", "secreto-de-entorno")
    sig_explicit, _ = WallapopSigner.generate_signature(
        "GET", "/api/v3/search?keywords=motu", timestamp=1700000000000, secret="c2VjcmV0by1leHBsaWNpdG8="
    )
    sig_env, _ = WallapopSigner.generate_signature("GET", "/api/v3/search?keywords=motu", timestamp=1700000000000)
    assert sig_explicit != sig_env


# --- Parseo de la estructura real de /api/v3/search (capturada en incursión) ---

REAL_ITEM_SAMPLE = {
    "id": "p6183prvg5z5",
    "title": "Masters of the Universe Origins Scare Glow",
    "price": {"amount": 28.0, "currency": "EUR"},
    "images": [
        {
            "id": "qjwe1nkv2n4j",
            "urls": {
                "small": "https://cdn.wallapop.com/images/x/small.jpg",
                "medium": "https://cdn.wallapop.com/images/x/medium.jpg",
                "big": "https://cdn.wallapop.com/images/x/big.jpg",
            },
        }
    ],
    "web_slug": "masters-of-the-universe-origins-scare-glow-1281596431",
}


def test_parse_wallapop_json_objects_extracts_offer():
    scraper = WallapopScraper()
    offers = scraper._parse_wallapop_json_objects([REAL_ITEM_SAMPLE])
    assert len(offers) == 1
    offer = offers[0]
    assert offer.product_name == "Masters of the Universe Origins Scare Glow"
    assert offer.price == 28.0
    assert offer.url == "https://es.wallapop.com/item/masters-of-the-universe-origins-scare-glow-1281596431"
    assert offer.image_url == "https://cdn.wallapop.com/images/x/big.jpg"
    assert offer.source_type == "Peer-to-Peer"


def test_parse_wallapop_json_objects_filters_junk_keywords():
    scraper = WallapopScraper()
    junk_item = dict(REAL_ITEM_SAMPLE, title="Camiseta Masters of the Universe", web_slug="camiseta-motu-123")
    offers = scraper._parse_wallapop_json_objects([junk_item])
    assert offers == []


def test_parse_wallapop_json_objects_skips_missing_price():
    scraper = WallapopScraper()
    no_price_item = dict(REAL_ITEM_SAMPLE)
    del no_price_item["price"]
    offers = scraper._parse_wallapop_json_objects([no_price_item])
    assert offers == []


@pytest.mark.network
@pytest.mark.asyncio
async def test_search_wallapop_v3_signed_smoke():
    """
    Smoke test opcional contra la API real. Requiere red (IP no vetada por WAF) y
    NO se ejecuta en CI por defecto (marcado @pytest.mark.network).

    Ejecutar manualmente con: pytest -m network tests/unit/test_wallapop_signed_api.py
    """
    from curl_cffi.requests import AsyncSession
    from src.infrastructure.scrapers.wallapop_signed_api import search_wallapop_v3_signed

    async with AsyncSession() as session:
        result = await search_wallapop_v3_signed(session, "masters of the universe origins", max_items=10)

    if result.blocked:
        pytest.skip("API firmada bloqueada por WAF desde esta IP (esperado en datacenter sin proxy).")

    assert isinstance(result.offers, list)
