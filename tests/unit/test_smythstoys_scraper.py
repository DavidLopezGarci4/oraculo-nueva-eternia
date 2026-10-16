import json
import pytest
from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper


def test_smythstoys_default_masters_search_url():
    scraper = SmythsToysScraper()
    assert "text=MASTERS" in scraper.search_url
    assert "brands=%5B%22Mattel%22%2C%22WWE%22%5D" in scraper.search_url
    assert "page=2" in scraper.search_url
    assert scraper._resolve_target_url("auto") == scraper.search_url


def test_smythstoys_parse_nuxt_data_devalue_and_vintage_guard():
    scraper = SmythsToysScraper()

    # Construct a realistic Nuxt 3 devalue flat array with:
    # 1. Valid Origins product (in stock)
    # 2. Valid WWE Masters product (out of stock)
    # 3. 1980s Vintage product (must be filtered out by check_is_vintage)
    nuxt_payload = [
        ["ShallowReactive", 1],
        {"products": 2},
        [3, 12, 21],
        # Item 1 (idx 3): Valid Origins figure
        {
            "code": 4,
            "name": 5,
            "url": 6,
            "metadata": 7,
            "productImage": 10,
            "stock": 11,
        },
        "234567",
        "Exklusiv Masters of the Universe Origins He-Man Actionfigur",
        "/de/de-de/spielzeug/masters-origins-he-man/p/234567",
        {"priceDetails": 8},
        {"value": 9},
        19.99,
        {"desktop": "https://image.smythstoys.com/original/desktop/234567.jpg"},
        {"stockLevelStatus": "inStock"},
        # Item 2 (idx 12): Valid WWE Masters figure (out of stock)
        {
            "code": 13,
            "name": 14,
            "url": 15,
            "metadata": 16,
            "productImage": 19,
            "stock": 20,
        },
        "234568",
        "Masters of the Universe WWE Rey Mysterio Actionfigur",
        "/de/de-de/spielzeug/wwe-rey-mysterio/p/234568",
        {"priceDetails": 17},
        {"value": 18},
        24.99,
        {"desktop": "/images/234568.jpg"},
        {"stockLevelStatus": "outOfStock"},
        # Item 3 (idx 21): 1980s Vintage item (must be excluded)
        {
            "code": 22,
            "name": 23,
            "url": 24,
            "metadata": 25,
        },
        "198401",
        "Masters of the Universe Skeletor Vintage 1982 Mattel Taiwan Original",
        "/de/de-de/spielzeug/skeletor-vintage-1982/p/198401",
        {"priceDetails": 26},
        {"value": 120.0},
    ]

    html = f'<html><body><script id="__NUXT_DATA__" type="application/json">{json.dumps(nuxt_payload)}</script></body></html>'
    offers = scraper._extract_offers_from_html(html, set())

    assert len(offers) == 2
    assert offers[0].product_name == "Origins He-Man Actionfigur"
    assert offers[0].price == 19.99
    assert offers[0].url == "https://www.smythstoys.com/de/de-de/spielzeug/masters-origins-he-man/p/234567"
    assert offers[0].image_url == "https://image.smythstoys.com/original/desktop/234567.jpg"
    assert offers[0].is_available is True

    assert offers[1].product_name == "WWE Rey Mysterio Actionfigur"
    assert offers[1].price == 24.99
    assert offers[1].image_url == "https://www.smythstoys.com/images/234568.jpg"
    assert offers[1].is_available is False


