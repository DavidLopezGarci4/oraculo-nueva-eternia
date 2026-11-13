"""
Adversarial Red Team Security & Governance Regression Suite (WU2).

Follows ODD RED -> GREEN discipline: written before remediation to reproduce
verified vulnerabilities across Auth/RBAC, SSRF/LFI, IDOR, Secrets/Logging,
CI/Docker hardening, Vintage ban, and Zero-Trust DB governance.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from pydantic import ValidationError
from sqlalchemy.engine import make_url

from src.application.services.gemini_card_service import GeminiCardService
from src.core.config import Settings
from src.domain.models import CollectionItemModel, ProductModel, UserModel
from src.interfaces.api import deps
from tests.conftest import API_KEY, _TestSession

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_rt01_username_cannot_escalate_to_admin_and_register_normalizes_case(client):
    """CRITICAL-01: Case/whitespace username collisions must not bypass checks or grant admin."""
    viewer_named_david = UserModel(
        id=9991,
        username="David",
        email="not-an-admin@example.com",
        role="viewer",
        is_active=True,
    )
    viewer_named_admin = UserModel(
        id=9992,
        username="ADMIN",
        email="fake-admin@example.com",
        role="viewer",
        is_active=True,
    )
    assert deps.is_admin(viewer_named_david) is False
    assert deps.is_admin(viewer_named_admin) is False

    # Public self-registration with reserved or whitespace-padded admin aliases must be blocked
    for candidate in ("admin", "ADMIN ", "david", " David "):
        resp = client.post(
            "/api/auth/register",
            json={
                "username": candidate,
                "email": f"escalate_{abs(hash(candidate))}@example.com",
                "password": "StrongPassword!123",
            },
        )
        assert resp.status_code in (400, 422), f"Allowed reserved/admin-like username: {candidate!r}"

    # Case-insensitive uniqueness must reject uppercase variant of existing viewer
    first = client.post(
        "/api/auth/register",
        json={
            "username": "CaseGuardHero",
            "email": "caseguard@example.com",
            "password": "StrongPassword!123",
        },
    )
    assert first.status_code == 200, first.text

    dup_user = client.post(
        "/api/auth/register",
        json={
            "username": " caseguardhero ",
            "email": "other-caseguard@example.com",
            "password": "StrongPassword!123",
        },
    )
    assert dup_user.status_code in (400, 422)

    dup_email = client.post(
        "/api/auth/register",
        json={
            "username": "OtherGuardHero",
            "email": "CASEGUARD@EXAMPLE.COM ",
            "password": "StrongPassword!123",
        },
    )
    assert dup_email.status_code in (400, 422)


def test_rt02_ssrf_and_arbitrary_file_read_blocked_in_safe_http_and_cards(client):
    """CRITICAL-02: safe_http & GeminiCardService must block private/metadata URLs & local file paths."""
    from src.core.safe_http import validate_public_url

    blocked_targets = [
        "http://127.0.0.1:8000/api/health",
        "http://localhost:8000/api/health",
        "http://169.254.169.254/opc/v2/instance/",
        "http://10.0.0.5/internal",
        "http://192.168.1.10/admin",
        "http://[::1]:8000/",
        "file:///app/.env",
        "ftp://example.com/file",
    ]
    for target in blocked_targets:
        with pytest.raises(ValueError):
            validate_public_url(target)

    # Arbitrary local path read in GeminiCardService._resolve_image_bytes must be rejected
    for malicious_ref in ("pyproject.toml", ".env", "../oraculo.db", "http://169.254.169.254/opc/v2/instance/"):
        with pytest.raises(ValueError):
            asyncio.run(GeminiCardService._resolve_image_bytes(malicious_ref, None))

    # /api/cards/ai-enhance must require authenticated JWT (not merely verify_device)
    resp = client.post(
        "/api/cards/ai-enhance",
        json={"product_name": "He-Man"},
    )
    assert resp.status_code in (401, 403)


def test_rt03_ci_workflows_have_no_expression_injection_and_prod_port_bound_to_localhost():
    """CRITICAL-03 & CRITICAL-04: No ${{ github.event.inputs.* }} in run: blocks and no 0.0.0.0:8000 in prod."""
    for wf_path in sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml")):
        data = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
        for job_name, job in (data.get("jobs") or {}).items():
            for step in job.get("steps") or []:
                run_script = step.get("run") or ""
                assert "github.event.inputs" not in run_script, (
                    f"{wf_path.name}::{job_name} interpolates github.event.inputs directly inside run:"
                )
                assert "${{ inputs." not in run_script, (
                    f"{wf_path.name}::{job_name} interpolates inputs.* directly inside run:"
                )

    compose = yaml.safe_load((REPO_ROOT / "docker-compose.prod.yml").read_text(encoding="utf-8"))
    ports = compose["services"]["backend"].get("ports") or []
    assert "8000:8000" not in [str(p).strip() for p in ports], (
        "Backend production port 8000 must be bound to 127.0.0.1:8000:8000, not 0.0.0.0!"
    )


def test_rt04_financial_idor_closed_on_dashboard_and_analytics(client, authorized_device_headers):
    """HIGH-05: Viewer or device-only caller must never read another user's manual prices/notes."""
    victim_creds = {"username": "idor_victim", "email": "idor_victim@test.com", "password": "VictimPass!123"}
    attacker_creds = {"username": "idor_attacker", "email": "idor_attacker@test.com", "password": "AttackerPass!123"}

    for creds in (victim_creds, attacker_creds):
        r = client.post("/api/auth/register", json=creds)
        assert r.status_code in (200, 400), r.text

    v_login = client.post("/api/auth/login", json={"email": victim_creds["email"], "password": victim_creds["password"]})
    a_login = client.post("/api/auth/login", json={"email": attacker_creds["email"], "password": attacker_creds["password"]})
    victim_id = v_login.json()["user"]["id"]
    attacker_bearer = {"Authorization": f"Bearer {a_login.json()['access_token']}"}
    attacker_headers = {**authorized_device_headers, **attacker_bearer}

    with _TestSession() as db:
        prod = ProductModel(
            name="RT04 Secret Purchase Figure",
            category="MOTU",
            sub_category="Origins",
            figure_id="RT04-SECRET",
            is_vintage=False,
            retail_price=22.0,
            avg_market_price=80.0,
        )
        db.add(prod)
        db.flush()
        db.add(
            CollectionItemModel(
                owner_id=victim_id,
                product_id=prod.id,
                acquired=True,
                condition="MOC",
                grading=9.5,
                purchase_price=199.99,
                notes="PRIVATE_VICTIM_NOTE_XYZ",
            )
        )
        db.commit()
        target_pid = prod.id

    # 1. Authenticated attacker targeting victim's user_id must get own empty portfolio
    stats_atk = client.get(f"/api/dashboard/stats?user_id={victim_id}", headers=attacker_headers)
    assert stats_atk.status_code == 200
    assert stats_atk.json()["financial"]["total_invested"] < 100.0

    hof_atk = client.get(f"/api/dashboard/hall-of-fame?user_id={victim_id}", headers=attacker_headers)
    assert hof_atk.status_code == 200
    assert "PRIVATE_VICTIM_NOTE_XYZ" not in hof_atk.text
    assert "199.99" not in hof_atk.text

    emi_atk = client.get(f"/api/analytics/market-index?period=3M&user_id={victim_id}", headers=attacker_headers)
    assert emi_atk.status_code == 200
    assert emi_atk.json().get("portfolio_metrics") is None

    # 2. Unauthenticated device-only caller (stripped JWT) targeting victim_id must see 0 invested & empty HOF
    stats_anon = client.get(f"/api/dashboard/stats?user_id={victim_id}", headers=authorized_device_headers)
    assert stats_anon.status_code == 200
    assert stats_anon.json()["financial"]["total_invested"] == 0.0

    hof_anon = client.get(f"/api/dashboard/hall-of-fame?user_id={victim_id}", headers=authorized_device_headers)
    assert hof_anon.status_code == 200
    assert hof_anon.json() == {
        "origins": {"top_value": [], "top_roi": []},
        "vintage": {"top_value": [], "top_roi": []},
    }

    opt_anon = client.post(
        "/api/cart/budget-optimize",
        json={"budget_limit": 50.0, "user_id": victim_id, "target_product_ids": [target_pid]},
        headers=authorized_device_headers,
    )
    assert opt_anon.status_code == 200


def test_rt05_secrets_redaction_and_fail_closed_env_config(client):
    """HIGH-08 & HIGH-09: Secrets scrubbed from logs and /api/system/audit; non-dev ENVs fail on defaults."""
    from src.core.logger import redact_sensitive_text

    sample = (
        "Request https://generativelanguage.googleapis.com/v1beta/models/x:generateContent?key=AIzaSuperSecret123 "
        "and https://api.telegram.org/bot123456:ABCDEF-SECRET/getUpdates "
        "and postgresql://postgres:MyDbSecret99@db.example.supabase.co:6543/postgres"
    )
    redacted = redact_sensitive_text(sample)
    assert "AIzaSuperSecret123" not in redacted
    assert "ABCDEF-SECRET" not in redacted
    assert "MyDbSecret99" not in redacted

    # /api/system/audit must hide password when DATABASE_URL contains credentials
    with patch("src.core.config.settings.DATABASE_URL", "postgresql://postgres:SupaSecret42@db.host:5432/postgres"):
        audit_resp = client.get("/api/system/audit", headers={"X-API-Key": API_KEY})
        assert audit_resp.status_code == 200
        assert "SupaSecret42" not in audit_resp.text
        parsed_db_url = audit_resp.json()["environment"]["DATABASE_URL"]
        assert parsed_db_url == make_url("postgresql://postgres:SupaSecret42@db.host:5432/postgres").render_as_string(hide_password=True)

    # Non-development ENVs (e.g. "prod", "staging") must refuse default insecure secrets
    from src.core.config import validate_environment_secrets

    for env_name in ("production", "prod", "staging"):
        insecure_settings = Settings(ENV=env_name, JWT_SECRET="oraculo-jwt-secret-CHANGE-IN-PRODUCTION")
        with pytest.raises(ValueError):
            validate_environment_secrets(insecure_settings)


def test_rt06_vintage_ban_enforced_in_manual_html_and_run_endpoint(client):
    """MEDIUM-10: AGENTS.md Rule 2 — manual Wallapop HTML & /scrapers/run reject 1980s/vintage inputs."""
    html_payload = """
    <html><body>
      <a href="/item/he-man-vintage-1982-123456">
        <p class="ItemCard__title">He-Man Vintage 1982 Mattel</p>
        <span class="ItemCard__price">95,00 €</span>
      </a>
    </body></html>
    """
    resp_html = client.post(
        "/api/scrapers/wallapop/import-manual-html",
        files={"file": ("wallapop.html", html_payload.encode("utf-8"), "text/html")},
        headers={"X-API-Key": API_KEY},
    )
    assert resp_html.status_code == 200, resp_html.text
    assert resp_html.json()["total_inserted"] == 0

    resp_run = client.post(
        "/api/scrapers/run",
        json={"spider_name": "Ebay.es", "query": "motu vintage 1984"},
        headers={"X-API-Key": API_KEY},
    )
    assert resp_run.status_code == 400


def test_rt07_security_headers_hashed_reset_token_and_showcase_wildcard_fix(client, test_user):
    """MEDIUM-14 & LOW-17: Security headers on API, hashed reset_token in DB, no % wildcard match."""
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.headers.get("X-Content-Type-Options") == "nosniff"
    assert health.headers.get("X-Frame-Options") == "DENY"
    assert health.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    # Showcase '%' wildcard must not match arbitrary existing users
    wildcard_resp = client.get("/api/public/showcase/%25")
    assert wildcard_resp.status_code == 404

    # Forgot password must store SHA-256 hash instead of plaintext token
    with patch("src.core.config.settings.DEBUG", True):
        fp = client.post("/api/auth/forgot-password", json={"email": test_user["email"]})
    assert fp.status_code == 200
    debug_token = fp.json().get("debug_token")
    assert debug_token
    with _TestSession() as db:
        u = db.query(UserModel).filter(UserModel.email == test_user["email"]).first()
        assert u is not None and u.reset_token is not None
        assert u.reset_token != debug_token, "reset_token was stored in plaintext instead of hashed!"

    # Reset must still succeed using the raw token
    rp = client.post("/api/auth/reset-password", json={"token": debug_token, "new_password": "NewViewerPass!123"})
    assert rp.status_code == 200

    # Restore fixture password so subsequent integration tests remain deterministic
    login_check = client.post("/api/auth/login", json={"email": test_user["email"], "password": "NewViewerPass!123"})
    assert login_check.status_code == 200
    with _TestSession() as db:
        from src.core.security import SecurityShield

        u = db.query(UserModel).filter(UserModel.email == test_user["email"]).first()
        u.hashed_password = SecurityShield.hash_password(test_user["password"])
        db.commit()


def test_rt08_products_refresh_image_requires_admin_and_static_images_ignore_pc_path(client, bearer, tmp_path):
    """HIGH-06 & MEDIUM-12: refresh-image must reject device-only caller; static images ignore viewer pc_image_path and image-paths requires admin."""
    r = client.post("/api/products/1/refresh-image")
    assert r.status_code == 403

    evil_dir = tmp_path / "host_secret_images"
    evil_dir.mkdir()
    (evil_dir / "99991.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")

    with _TestSession() as db:
        u = db.query(UserModel).filter(UserModel.email == "viewer@test.com").first()
        assert u is not None
        u.pc_image_path = str(evil_dir)
        uid = u.id
        db.commit()

    import src.interfaces.api.main as main_mod

    main_mod.invalidate_user_image_paths_cache(uid)
    img_resp = client.get(f"/api/static/images/99991.webp?user_id={uid}")
    assert img_resp.status_code == 404

    img_custom_resp = client.get(f"/api/static/images/99991.webp?source=custom&user_id={uid}")
    assert img_custom_resp.status_code == 404

    upd_resp = client.post(
        f"/api/users/{uid}/image-paths",
        headers=bearer,
        json={"pc_path": str(evil_dir), "mobile_path": None},
    )
    assert upd_resp.status_code == 403


def test_rt09_non_ascii_auth_and_prod_debug_and_reset_email_redaction(client, caplog):
    """Non-ASCII auth headers must return 403 cleanly; DEBUG=True blocked in prod; reset token never logged."""
    from src.infrastructure.email_service import EmailService

    # 1. Non-ASCII X-API-Key / X-Extension-Key must return 403 cleanly, not 500 TypeError
    from fastapi import HTTPException
    from starlette.requests import Request
    from src.core.security import SecurityShield

    assert SecurityShield.safe_compare_digest("clave-ñ-€", "clave-ñ-€") is True
    assert SecurityShield.safe_compare_digest("clave-ñ-€", "otra-ñ") is False

    with pytest.raises(HTTPException) as exc_api:
        deps.verify_api_key("clave-inválida-ñ-€")
    assert exc_api.value.status_code == 403

    dummy_req = Request({"type": "http", "headers": [], "client": ("198.51.100.77", 12345)})
    with pytest.raises(HTTPException) as exc_ext:
        deps.verify_wallapop_import(
            dummy_req,
            x_extension_key="clave-extensión-ñ-€",
            x_device_id=None,
            x_device_name="Test",
        )
    assert exc_ext.value.status_code == 403

    r_api = client.get("/api/purgatory", headers={"X-API-Key": "invalid-ascii-key"})
    assert r_api.status_code == 403

    # 2. DEBUG=True forbidden in production / staging via validate_environment_secrets
    from src.core.config import validate_environment_secrets

    cfg_debug_prod = Settings(
        ENV="production",
        DEBUG=True,
        ORACULO_API_KEY="StrongKeyValueForProdTest123!",
        SECRET_KEY="StrongSecretKeyForProdTest123!",
        CORS_ORIGINS="https://oraculo.example.com",
    )
    with pytest.raises(ValueError, match="DEBUG=True"):
        validate_environment_secrets(cfg_debug_prod)

    # 2b. SSRF peer IP verification must read httpcore's "server_addr" even if "peername" is None
    import httpx
    from src.core.safe_http import _verify_peer_ip

    class _FakeHttpcoreStream:
        def __init__(self, server_addr):
            self._server_addr = server_addr

        def get_extra_info(self, info: str):
            return self._server_addr if info == "server_addr" else None

    for bad_ip in ("127.0.0.1", "169.254.169.254"):
        fake_resp = httpx.Response(
            200,
            extensions={"network_stream": _FakeHttpcoreStream((bad_ip, 80))},
        )
        with pytest.raises(ValueError, match="no pública"):
            _verify_peer_ip(fake_resp)

    ok_resp = httpx.Response(
        200,
        extensions={"network_stream": _FakeHttpcoreStream(("93.184.216.34", 443))},
    )
    _verify_peer_ip(ok_resp)

    # 3. EmailService must never log raw reset token when SMTP unconfigured, and must escape username HTML
    raw_token = "reset-secret-token-should-not-log-777"
    with (
        patch("src.infrastructure.email_service.settings.SMTP_HOST", ""),
        patch("src.infrastructure.email_service.settings.SMTP_USER", ""),
        caplog.at_level("WARNING"),
    ):
        ok = EmailService.send_reset_email("user@example.com", "evil<b>user</b>", raw_token)
        assert ok is False
    assert raw_token not in caplog.text

    captured_html = []

    class _DummySMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            pass

        def login(self, user, pwd):
            pass

        def send_message(self, msg):
            html_part = msg.get_payload(1).get_payload(decode=True).decode("utf-8")
            captured_html.append(html_part)

    with (
        patch("src.infrastructure.email_service.settings.SMTP_HOST", "smtp.example.com"),
        patch("src.infrastructure.email_service.settings.SMTP_USER", "bot@example.com"),
        patch("src.infrastructure.email_service.settings.SMTP_PASS", "secret"),
        patch("src.infrastructure.email_service.smtplib.SMTP", _DummySMTP),
    ):
        ok_smtp = EmailService.send_reset_email("user@example.com", "<script>xss</script>", "tok123")
        assert ok_smtp is True
    assert captured_html
    assert "&lt;script&gt;xss&lt;/script&gt;" in captured_html[0]
    assert "<script>xss</script>" not in captured_html[0]


def test_rt10_vintage_ban_across_wallapop_jobs_scrapers_and_telegram_html(client, test_user):
    """Vintage searches must be rejected everywhere and Telegram HTML notifications must escape payloads."""
    from unittest.mock import AsyncMock

    from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
    from src.infrastructure.scrapers.wallapop_manual_scraper import WallapopManualScraper
    from src.infrastructure.scrapers.wallapop_scraper import WallapopScraper
    from src.infrastructure.services.telegram_service import TelegramService

    # 1. Authenticate admin for /api/wallapop/jobs
    from tests.conftest import _TestSession

    with _TestSession() as db:
        u = db.query(UserModel).filter(UserModel.email == test_user["email"]).first()
        u.role = "admin"
        db.commit()

    login_r = client.post(
        "/api/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    assert login_r.status_code == 200
    token = login_r.json()["access_token"]

    r_job = client.post(
        "/api/wallapop/jobs",
        json={"query": "he-man vintage 1983 mattel"},
        headers={"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"},
    )
    assert r_job.status_code == 400

    # Restore role
    with _TestSession() as db:
        u = db.query(UserModel).filter(UserModel.email == test_user["email"]).first()
        u.role = "viewer"
        db.commit()

    # 2. Scraper direct guards
    assert asyncio.run(AmazonScraper().search("skeletor vintage 1984")) == []
    assert asyncio.run(WallapopScraper().search("motu años 80")) == []
    assert asyncio.run(WallapopManualScraper().search("he-man 1982 vintage")) == []

    # 3. Telegram HTML escaping across alert methods
    tg = TelegramService()
    tg.enabled = True
    tg.bot_token = "dummy-token"
    tg.chat_id = "12345"
    sent_payloads = []

    async def _fake_send(msg, **kwargs):
        sent_payloads.append(msg)
        return True

    with patch.object(tg, "send_message", side_effect=_fake_send):
        asyncio.run(
            tg.send_deal_alert(
                product_name="Skeletor <img src=x onerror=alert(1)>",
                price=12.0,
                shop_name="Shop & Co <b>Test</b>",
                url='https://example.com/?a=1&b="2"',
            )
        )
        asyncio.run(
            tg.send_wishlist_alert(
                chat_id="12345",
                product_name="Man-At-Arms <tag>",
                price=15.0,
                shop_name="Amazon <ES>",
                url='https://example.com/"quote"',
            )
        )
        asyncio.run(
            tg.send_bargain_hunt_alert(
                product_name="He-Man <x>",
                item_title="Item <script>bad()</script>",
                price=10.0,
                landed_price=15.0,
                benchmark_price=25.0,
                savings_pct=40.0,
                shop_name="Vinted <ES>",
                url='https://vinted.example/item?q="xss"',
            )
        )

    assert len(sent_payloads) == 3
    joined = "\n".join(sent_payloads)
    assert "<script>" not in joined
    assert "<img " not in joined
    assert "&lt;img src=x onerror=alert(1)&gt;" in joined
    assert "&lt;script&gt;bad()&lt;/script&gt;" in joined
