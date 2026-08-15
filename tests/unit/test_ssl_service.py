from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from src.application.services.ssl_service import SSLService


def _generate_test_cert_pem(valid_from: datetime, valid_until: datetime, domain: str = "oraculo-eternia.duckdns.org") -> bytes:
    """Genera un certificado X.509 PEM sintético para tests unitarios."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Let's Encrypt Test"),
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(valid_from)
        .not_valid_after(valid_until)
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(domain)]), critical=False)
        .sign(key, hashes.SHA256())
    )
    from cryptography.hazmat.primitives import serialization
    return cert.public_bytes(serialization.Encoding.PEM)


def test_parse_x509_cert():
    now = datetime.now(timezone.utc).replace(microsecond=0)
    valid_from = now - timedelta(days=10)
    valid_until = now + timedelta(days=80)
    
    pem_bytes = _generate_test_cert_pem(valid_from, valid_until, "oraculo-eternia.duckdns.org")
    parsed = SSLService._parse_x509_cert(pem_bytes)

    assert parsed["domain"] == "oraculo-eternia.duckdns.org"
    assert parsed["issuer"] == "Let's Encrypt Test"
    assert parsed["valid_from"] == valid_from
    assert parsed["valid_until"] == valid_until


def test_get_certificate_status_active():
    now = datetime.now(timezone.utc).replace(microsecond=0)
    valid_from = now - timedelta(days=30)
    valid_until = now + timedelta(days=60)  # Quedan 60 días
    pem_bytes = _generate_test_cert_pem(valid_from, valid_until)

    with patch.object(SSLService, "_find_cert_path") as mock_find, \
         patch("pathlib.Path.read_bytes", return_value=pem_bytes):
        mock_path = MagicMock()
        mock_path.read_bytes.return_value = pem_bytes
        mock_find.return_value = mock_path

        status = SSLService.get_certificate_status()

        assert status["domain"] == "oraculo-eternia.duckdns.org"
        assert status["status"] == "ACTIVE"
        assert status["is_valid"] is True
        assert status["days_remaining"] >= 59
        assert status["source"] == "disk"
        # Recomendación de renovación = fecha fin - 14 días
        expected_renewal = valid_until - timedelta(days=14)
        assert status["next_renewal_recommended"] == expected_renewal


def test_get_certificate_status_expiring_soon():
    now = datetime.now(timezone.utc)
    valid_from = now - timedelta(days=80)
    valid_until = now + timedelta(days=5)  # Quedan 5 días (menor o igual a 14)
    pem_bytes = _generate_test_cert_pem(valid_from, valid_until)

    with patch.object(SSLService, "_find_cert_path") as mock_find:
        mock_path = MagicMock()
        mock_path.read_bytes.return_value = pem_bytes
        mock_find.return_value = mock_path

        status = SSLService.get_certificate_status()

        assert status["status"] == "EXPIRING_SOON"
        assert status["is_valid"] is True
        assert 0 < status["days_remaining"] <= 5


def test_get_certificate_status_expired():
    now = datetime.now(timezone.utc)
    valid_from = now - timedelta(days=90)
    valid_until = now - timedelta(days=2)  # Expiró hace 2 días
    pem_bytes = _generate_test_cert_pem(valid_from, valid_until)

    with patch.object(SSLService, "_find_cert_path") as mock_find:
        mock_path = MagicMock()
        mock_path.read_bytes.return_value = pem_bytes
        mock_find.return_value = mock_path

        status = SSLService.get_certificate_status()

        assert status["status"] == "EXPIRED"
        assert status["is_valid"] is False
        assert status["days_remaining"] < 0


def test_get_certificate_status_fallback():
    with patch.object(SSLService, "_find_cert_path", return_value=None), \
         patch.object(SSLService, "_fetch_live_tls_cert", return_value=None):
        status = SSLService.get_certificate_status()

        assert status["status"] == "UNKNOWN"
        assert status["is_valid"] is False
        assert status["source"] == "fallback"
        assert status["domain"] == SSLService.DEFAULT_DOMAIN


@pytest.mark.asyncio
async def test_renew_ssl_certificate():
    with patch("src.core.security.SecurityShield.send_telegram_alert", new_callable=AsyncMock) as mock_alert, \
         patch.object(SSLService, "get_certificate_status", return_value={"status": "ACTIVE", "days_remaining": 60, "is_valid": True}):
        
        result = await SSLService.renew_ssl_certificate(force=True)

        assert result["status"] == "success"
        assert "message" in result
        mock_alert.assert_called_once()
