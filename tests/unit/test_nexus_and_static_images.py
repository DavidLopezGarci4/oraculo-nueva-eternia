"""
WU1 RED -> GREEN tests: Static image routing, local catalog rescue,
Nginx/CSP/Docker governance, and Nexus image injection hygiene.
"""
from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.domain.models import Base, OfferModel, PendingMatchModel, ProductModel, UserModel
from tests.conftest import _TestSession


REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_image_bytes(fmt: str = "JPEG", mode: str = "RGB", size=(8, 8)) -> bytes:
    color = (180, 128) if mode == "LA" else (220, 40, 40)
    img = Image.new(mode, size, color=color)
    buf = io.BytesIO()
    img.save(buf, fmt)
    return buf.getvalue()


def test_nginx_and_docker_compose_image_proxy_and_csp_governance():
    nginx_prod = (REPO_ROOT / "frontend" / "nginx.conf").read_text(encoding="utf-8")
    nginx_local = (REPO_ROOT / "frontend" / "nginx.local.conf").read_text(encoding="utf-8")
    compose_local = (REPO_ROOT / "docker-compose.local-prod.yml").read_text(encoding="utf-8")

    assert "location ^~ /api/" in nginx_prod, "nginx.conf must use ^~ so static regex does not hijack /api/static/images/*.webp"
    assert "location ^~ /api/" in nginx_local, "nginx.local.conf must use ^~ for /api/ prefix parity"
    assert "connect-src 'self' https://*.supabase.co" in nginx_prod, "nginx.conf CSP connect-src must permit Supabase Storage"
    assert "SUPABASE_URL=" in compose_local
    assert "SUPABASE_SERVICE_ROLE_KEY=" in compose_local


def test_static_images_extensionless_and_webp_routes_serve_cached_file(client, tmp_path):
    cache_file = tmp_path / "88101.webp"
    cache_file.write_bytes(_make_image_bytes("WEBP"))

    with patch("src.interfaces.api.main.settings.IMAGE_CACHE_DIR", str(tmp_path)):
        resp_no_ext = client.get("/api/static/images/88101?source=cache")
        resp_webp = client.get("/api/static/images/88101.webp?source=cache")

    assert resp_no_ext.status_code == 200
    assert resp_webp.status_code == 200
    assert resp_no_ext.content[:4] == b"RIFF"
    assert resp_no_ext.content == resp_webp.content


def test_static_image_rescues_from_local_catalog_before_remote(client, tmp_path):
    catalog_dir = tmp_path / "catalog" / "data" / "MOTU" / "images"
    catalog_dir.mkdir(parents=True)
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    # Local catalog still stores .jpg while DB has a broken .webp Supabase URL
    (catalog_dir / "rowdy-roddy-piper-12022.jpg").write_bytes(_make_image_bytes("JPEG"))

    with _TestSession() as db:
        prod = ProductModel(
            name='"Rowdy" Roddy Piper',
            figure_id="12022",
            category="Masters of the Universe",
            sub_category="Masters of the WWE Universe Action Figures",
            is_vintage=False,
            image_url="https://example.supabase.co/storage/v1/object/public/motu-catalog/rowdy-roddy-piper-12022.webp",
        )
        db.add(prod)
        db.commit()
        pid = prod.id

    with patch("src.interfaces.api.main.settings.IMAGE_CACHE_DIR", str(cache_dir)), \
         patch("src.interfaces.api.main._PROJECT_ROOT", tmp_path / "catalog", create=True), \
         patch("src.interfaces.api.main._fetch_and_cache_product_image") as mock_remote:
        resp = client.get(f"/api/static/images/{pid}?source=cache")

    assert resp.status_code == 200
    assert resp.content[:4] == b"RIFF"
    assert (cache_dir / f"{pid}.webp").exists()
    mock_remote.assert_not_called()


def test_candidate_image_urls_include_supabase_jpg_sibling_and_https_upgrade():
    from src.interfaces.api.main import _load_product_candidate_image_urls

    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)

    with TestSession() as db:
        prod = ProductModel(
            id=501,
            name="Cody Rhodes",
            figure_id="14271",
            image_url="https://abc.supabase.co/storage/v1/object/public/motu-catalog/cody-rhodes-14271.webp",
        )
        db.add(prod)
        db.flush()
        db.add(
            OfferModel(
                product_id=501,
                shop_name="Wallapop",
                price=25.0,
                url="https://es.wallapop.com/item/cody-1",
                image_url="http://cdn.example.com/cody-offer.jpg",
            )
        )
        db.add(
            PendingMatchModel(
                scraped_name="Cody",
                price=25.0,
                url="https://es.wallapop.com/item/cody-1",
                shop_name="Wallapop",
                image_url="https://cdn.example.com/cody-pending.jpg",
            )
        )
        db.commit()

    with patch("src.interfaces.api.main._resolve_session_cloud", return_value=TestSession):
        candidates = _load_product_candidate_image_urls(501)

    assert candidates[0] == "https://abc.supabase.co/storage/v1/object/public/motu-catalog/cody-rhodes-14271.webp"
    assert "https://abc.supabase.co/storage/v1/object/public/motu-catalog/cody-rhodes-14271.jpg" in candidates
    assert "https://abc.supabase.co/storage/v1/object/public/motu-catalog/cody-rhodes-14271.png" in candidates
    assert "https://cdn.example.com/cody-offer.jpg" in candidates
    assert "https://cdn.example.com/cody-pending.jpg" in candidates
    assert candidates.index("https://cdn.example.com/cody-offer.jpg") < candidates.index("http://cdn.example.com/cody-offer.jpg")


def test_nexus_phase0_normalizes_runner_paths_handles_la_mode_and_preserves_existing_urls(tmp_path, monkeypatch):
    from scripts import phase0_migration, phase0_vintage_migration

    fake_root = tmp_path / "repo"
    images_dir = fake_root / "data" / "MOTU" / "images"
    vintage_dir = fake_root / "data" / "MOTU" / "vintage_images"
    cache_dir = tmp_path / "image_cache"
    images_dir.mkdir(parents=True)
    vintage_dir.mkdir(parents=True)
    cache_dir.mkdir()

    # Sibling .jpg exists locally while Excel stores GH Actions /home/runner/work/.../*.webp
    jpg_file = images_dir / "the-american-nightmare-cody-rhodes-14271.jpg"
    jpg_file.write_bytes(_make_image_bytes("JPEG", mode="RGB"))

    vint_jpg = vintage_dir / "he-man-vintage-1982.jpg"
    vint_jpg.write_bytes(_make_image_bytes("JPEG", mode="RGB"))

    monkeypatch.setattr(phase0_migration, "root_dir", fake_root)
    monkeypatch.setattr(phase0_vintage_migration, "root_dir", fake_root)
    monkeypatch.setattr(phase0_migration.settings, "IMAGE_CACHE_DIR", str(cache_dir))
    monkeypatch.setattr(phase0_vintage_migration.settings, "IMAGE_CACHE_DIR", str(cache_dir))
    monkeypatch.setattr(phase0_migration.settings, "SUPABASE_URL", "https://demo.supabase.co")
    monkeypatch.setattr(phase0_migration, "download_missing_image", lambda url, path: False)

    resolved = phase0_migration.resolve_local_image_path(
        "/home/runner/work/oraculo-nueva-eternia/oraculo-nueva-eternia/data/MOTU/images/the-american-nightmare-cody-rhodes-14271.webp",
        "https://actionfigure411.com/img/cody.jpg",
    )
    assert resolved is not None
    assert Path(resolved) == jpg_file

    resolved_v = phase0_vintage_migration.resolve_local_image_path(
        "/home/runner/work/oraculo-nueva-eternia/oraculo-nueva-eternia/data/MOTU/vintage_images/he-man-vintage-1982.webp",
        "https://actionfigure411.com/img/vint.jpg",
    )
    assert resolved_v is not None
    assert Path(resolved_v) == vint_jpg

    # Mode 'LA' must not crash with IndexError in cache_image_locally
    la_png = tmp_path / "grayscale_alpha.png"
    la_png.write_bytes(_make_image_bytes("PNG", mode="LA"))
    phase0_migration.cache_image_locally(str(la_png), 9901)
    assert (cache_dir / "9901.webp").exists()

    # Existing product .jpg URL must NOT be blindly overwritten to unverified .webp in Step 2
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    import openpyxl

    excel_file = tmp_path / "lista_MOTU.xlsx"
    headers = [
        "Adquirido", "Name", "Wave", "Year", "Retail", "Avg", "P25",
        "Currency", "Image Path", "Image URL", "Detail Link", "Figure ID",
    ]
    rows = [
        [
            "No",
            '"The American Nightmare" Cody Rhodes',
            "1",
            "2021",
            "$19.99",
            "$30.00",
            "$25.00",
            "USD",
            "/home/runner/work/oraculo-nueva-eternia/oraculo-nueva-eternia/data/MOTU/images/the-american-nightmare-cody-rhodes-14271.webp",
            "https://actionfigure411.com/cody.jpg",
            "https://actionfigure411.com/cody",
            "14271",
        ],
        [
            "No",
            "New Figure",
            "2",
            "2024",
            "$19.99",
            "$20.00",
            "$18.00",
            "USD",
            "data/MOTU/images/new-figure-55555.jpg",
            "https://actionfigure411.com/new-figure.jpg",
            "https://actionfigure411.com/new",
            "55555",
        ],
    ]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Origins_Checklist"
    ws.append(["Origins Checklist Title"])
    ws.append(headers)
    for r in rows:
        ws.append(r)
    wb.save(excel_file)

    class _OpenpyxlExcelFile:
        def __init__(self, path):
            self._wb = openpyxl.load_workbook(path, data_only=True)
            self.sheet_names = list(self._wb.sheetnames)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            self._wb.close()
            return False

    def _openpyxl_read_excel(xl, sheet_name, header=1):
        sheet_rows = list(xl._wb[sheet_name].iter_rows(values_only=True))
        return pd.DataFrame(sheet_rows[header + 1 :], columns=sheet_rows[header])

    monkeypatch.setattr(phase0_migration.pd, "ExcelFile", _OpenpyxlExcelFile)
    monkeypatch.setattr(phase0_migration.pd, "read_excel", _openpyxl_read_excel)

    with Session() as db:
        db.add(UserModel(username="David", email="david@test.com", hashed_password="pw", role="admin"))
        db.add(
            ProductModel(
                name='"The American Nightmare" Cody Rhodes',
                figure_id="14271",
                sub_category="Origins",
                image_url="https://demo.supabase.co/storage/v1/object/public/motu-catalog/the-american-nightmare-cody-rhodes-14271.jpg",
            )
        )
        db.commit()

        phase0_migration.migrate_excel_to_db(str(excel_file), db)

        cody = db.query(ProductModel).filter_by(figure_id="14271").first()
        new_fig = db.query(ProductModel).filter_by(figure_id="55555").first()

        assert cody.image_url.endswith(".jpg"), f"Expected existing .jpg URL preserved, got {cody.image_url}"
        assert (cache_dir / f"{cody.id}.webp").exists()
        assert new_fig.image_url == "https://actionfigure411.com/new-figure.jpg"


def test_storage_service_reencodes_fake_webp_with_jpeg_magic_bytes(tmp_path):
    from src.application.services.storage_service import StorageService

    fake_webp = tmp_path / "cody-rhodes-14271.webp"
    fake_webp.write_bytes(_make_image_bytes("JPEG"))

    uploaded_payloads: list[tuple[str, bytes, dict]] = []

    fake_bucket = MagicMock()

    def _capture_upload(path_in_bucket, file_obj, file_options=None):
        uploaded_payloads.append((path_in_bucket, file_obj.read(), file_options or {}))

    fake_bucket.upload.side_effect = _capture_upload
    fake_bucket.get_public_url.side_effect = lambda p: f"https://demo.supabase.co/storage/v1/object/public/motu-catalog/{p}"

    storage = StorageService.__new__(StorageService)
    storage.bucket_name = "motu-catalog"
    storage.storage_disabled = False
    storage.client = MagicMock()
    storage.client.storage.from_.return_value = fake_bucket

    mapping = storage.upload_all_local_images(str(tmp_path))

    assert isinstance(mapping, dict)
    assert mapping["cody-rhodes-14271"] == "https://demo.supabase.co/storage/v1/object/public/motu-catalog/cody-rhodes-14271.webp"
    assert len(uploaded_payloads) == 1
    _, data_bytes, opts = uploaded_payloads[0]
    assert data_bytes[:4] == b"RIFF" and data_bytes[8:12] == b"WEBP"
    assert opts.get("content-type") == "image/webp"
