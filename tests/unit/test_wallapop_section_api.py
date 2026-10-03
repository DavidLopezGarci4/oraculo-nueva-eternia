"""
Tests unitarios (offline) para el motor orgánico de búsqueda de Wallapop (/api/v3/search/section).
Implementa validación TDD para el puerto desde PokeCardTrack.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.infrastructure.scrapers.wallapop_section_api import (
    build_section_params,
    build_section_headers,
    extract_image_url,
    parse_section_items,
    search_wallapop_section,
    SectionSearchResult,
)


def test_build_section_params():
    # Búsqueda inicial
    params = build_section_params("masters origins")
    assert params["keywords"] == "masters origins"
    assert params["source"] == "deep_link"
    assert params["latitude"] == "40.4153"
    assert params["longitude"] == "-3.694"
    assert params["order_by"] == "most_relevance"
    assert params["search_country"] == "ES"
    assert params["section_type"] == "organic_search_results"
    assert "next_page" not in params

    # Paginación
    page_params = build_section_params("masters origins", next_page="token_abc_123")
    assert page_params == {"next_page": "token_abc_123"}


def test_build_section_headers():
    headers = build_section_headers()
    assert headers["x-deviceos"] == "0"
    assert "es.wallapop.com" in headers["Referer"]
    assert "es.wallapop.com" in headers["Origin"]
    assert "Chrome/128" in headers["User-Agent"]


def test_extract_image_url():
    # Caso 1: Estructura estándar con urls (prioridad medium > big > small)
    item_medium = {
        "images": [
            {
                "urls": {
                    "small": "https://cdn.wallapop.com/small.jpg",
                    "medium": "https://cdn.wallapop.com/medium.jpg",
                    "big": "https://cdn.wallapop.com/big.jpg",
                }
            }
        ]
    }
    assert extract_image_url(item_medium) == "https://cdn.wallapop.com/medium.jpg"

    # Caso 2: Solo big y small
    item_big = {
        "images": [
            {
                "urls": {
                    "small": "https://cdn.wallapop.com/small.jpg",
                    "big": "https://cdn.wallapop.com/big.jpg",
                }
            }
        ]
    }
    assert extract_image_url(item_big) == "https://cdn.wallapop.com/big.jpg"

    # Caso 3: Solo small
    item_small = {
        "images": [
            {
                "urls": {
                    "small": "https://cdn.wallapop.com/small.jpg",
                }
            }
        ]
    }
    assert extract_image_url(item_small) == "https://cdn.wallapop.com/small.jpg"

    # Caso 4: URLs en formato plano o fallback legacy
    item_legacy = {"images": [{"original": "https://cdn.wallapop.com/orig.jpg"}]}
    assert extract_image_url(item_legacy) == "https://cdn.wallapop.com/orig.jpg"

    # Caso 5: Sin imágenes
    assert extract_image_url({}) is None
    assert extract_image_url({"images": []}) is None


def test_parse_section_items():
    raw_items = [
        {
            "id": "item1",
            "title": "He-Man MOTU Origins Nuevo",
            "price": {"amount": 22.5, "currency": "EUR"},
            "web_slug": "he-man-motu-origins-nuevo-item1",
            "images": [
                {
                    "urls": {
                        "medium": "https://cdn.wallapop.com/img1.jpg"
                    }
                }
            ]
        },
        {
            # Debe descartarse por palabra clave basura
            "id": "item2",
            "title": "Camiseta He-Man Masters del Universo",
            "price": {"amount": 15.0, "currency": "EUR"},
            "web_slug": "camiseta-heman-item2",
            "images": []
        },
        {
            # Debe descartarse por precio inválido (<= 0)
            "id": "item3",
            "title": "Skeletor Origins",
            "price": {"amount": 0.0, "currency": "EUR"},
            "web_slug": "skeletor-item3",
        },
        {
            # Precio plano numérico
            "id": "item4",
            "title": "Man-At-Arms Origins",
            "price": 24.0,
            "web_slug": "man-at-arms-item4",
            "images": [{"urls": {"big": "https://cdn.wallapop.com/img4.jpg"}}]
        }
    ]

    offers = parse_section_items(raw_items, shop_name="Wallapop")
    assert len(offers) == 2
    assert offers[0].product_name == "He-Man MOTU Origins Nuevo"
    assert offers[0].price == 22.5
    assert offers[0].url == "https://es.wallapop.com/item/he-man-motu-origins-nuevo-item1"
    assert offers[0].image_url == "https://cdn.wallapop.com/img1.jpg"
    assert offers[0].shop_name == "Wallapop"
    assert offers[0].source_type == "Peer-to-Peer"
    assert offers[0].sale_type == "Fixed_P2P"

    assert offers[1].product_name == "Man-At-Arms Origins"
    assert offers[1].price == 24.0
    assert offers[1].image_url == "https://cdn.wallapop.com/img4.jpg"


@pytest.mark.asyncio
async def test_search_wallapop_section_success():
    session = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "section": {
                "items": [
                    {
                        "id": "item10",
                        "title": "Trap Jaw MOTU Origins",
                        "price": {"amount": 35.0, "currency": "EUR"},
                        "web_slug": "trap-jaw-item10",
                        "images": [{"urls": {"medium": "https://cdn.wallapop.com/trapjaw.jpg"}}]
                    }
                ]
            }
        },
        "meta": {
            "next_page": "token_next_xyz"
        }
    }
    session.get.return_value = mock_resp

    result = await search_wallapop_section(session, "trap jaw origins")
    assert isinstance(result, SectionSearchResult)
    assert not result.blocked
    assert len(result.offers) == 1
    assert result.offers[0].product_name == "Trap Jaw MOTU Origins"
    assert result.offers[0].price == 35.0
    assert result.next_page == "token_next_xyz"

    # Verificar llamada GET con impersonate chrome124
    session.get.assert_called_once()
    args, kwargs = session.get.call_args
    assert kwargs.get("impersonate") == "chrome124"
    assert kwargs.get("headers")["x-deviceos"] == "0"


@pytest.mark.asyncio
async def test_search_wallapop_section_blocked():
    session = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    session.get.return_value = mock_resp

    result = await search_wallapop_section(session, "origins")
    assert result.blocked
    assert len(result.offers) == 0
    assert result.next_page is None
