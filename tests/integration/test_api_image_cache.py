"""
Tests for the on-demand image cache population added in Fase AAA-4.2 (B.7):
main.py::_fetch_and_cache_product_image downloads a product's remote
image_url, converts it to WebP with Pillow, and saves it into
IMAGE_CACHE_DIR the first time it's requested — closing the gap where
images discovered by the live shop scrapers were never converted (only the
old Excel-importer path was).

These tests exercise the function directly (not through the FastAPI
TestClient) because it does its own `from ... import SessionCloud` inside
the function body — a throwaway in-memory session is patched in directly,
independent of the shared conftest.py session-scoped client fixture.
"""
import asyncio
import io
from unittest.mock import AsyncMock, patch

from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.domain.models import Base, ProductModel


def _make_test_session(seed_product: bool = True):
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    if seed_product:
        with TestSession() as db:
            db.add(ProductModel(id=1, name="Test Figure", image_url="https://shop.example.com/img.jpg"))
            db.commit()
    return TestSession


def _fake_source_image_bytes() -> bytes:
    """A tiny real JPEG, standing in for whatever format the shop serves."""
    img = Image.new("RGB", (4, 4), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    return buf.getvalue()


class _FakeResponse:
    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self):
        pass


def test_downloads_converts_and_caches_as_webp(tmp_path):
    from src.interfaces.api.main import _fetch_and_cache_product_image

    TestSession = _make_test_session()
    fake_response = _FakeResponse(_fake_source_image_bytes())

    with patch("src.infrastructure.database_cloud.SessionCloud", TestSession), \
         patch("src.core.config.settings.IMAGE_CACHE_DIR", str(tmp_path)), \
         patch("httpx.AsyncClient.get", new=AsyncMock(return_value=fake_response)):
        result = asyncio.run(_fetch_and_cache_product_image(1))

    expected_path = str(tmp_path / "1.webp")
    assert result == expected_path
    assert (tmp_path / "1.webp").exists()
    with Image.open(expected_path) as cached_img:
        assert cached_img.format == "WEBP"


def test_returns_none_when_product_has_no_image_url(tmp_path):
    from src.interfaces.api.main import _fetch_and_cache_product_image

    TestSession = _make_test_session(seed_product=False)
    with TestSession() as db:
        db.add(ProductModel(id=2, name="No Image Figure", image_url=None))
        db.commit()

    with patch("src.infrastructure.database_cloud.SessionCloud", TestSession):
        result = asyncio.run(_fetch_and_cache_product_image(2))

    assert result is None


def test_returns_none_for_nonexistent_product(tmp_path):
    from src.interfaces.api.main import _fetch_and_cache_product_image

    TestSession = _make_test_session()  # only has product id=1
    with patch("src.infrastructure.database_cloud.SessionCloud", TestSession):
        result = asyncio.run(_fetch_and_cache_product_image(999))

    assert result is None


def test_returns_none_and_does_not_crash_on_download_failure(tmp_path):
    from src.interfaces.api.main import _fetch_and_cache_product_image

    TestSession = _make_test_session()
    with patch("src.infrastructure.database_cloud.SessionCloud", TestSession), \
         patch("src.core.config.settings.IMAGE_CACHE_DIR", str(tmp_path)), \
         patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=Exception("network down"))):
        result = asyncio.run(_fetch_and_cache_product_image(1))

    assert result is None
    assert not (tmp_path / "1.webp").exists()
