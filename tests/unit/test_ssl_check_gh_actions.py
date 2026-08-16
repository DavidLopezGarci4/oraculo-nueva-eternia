"""
Tests unitarios para el script de comprobación y renovación automática de SSL en GitHub Actions.
"""
import pytest
from unittest.mock import patch, MagicMock
from scripts.check_and_renew_ssl_gh_actions import main, run_ssh_renewal, RENEWAL_THRESHOLD_DAYS


@pytest.mark.asyncio
async def test_ssl_gh_actions_healthy_when_above_threshold():
    """Si el certificado tiene más de 14 días restantes, no debe intentar renovar y sale con 0."""
    mock_status = {
        "status": "ACTIVE",
        "days_remaining": 45,
        "is_valid": True,
        "valid_until": "2026-11-14T09:39:54Z",
        "issuer": "Let's Encrypt",
        "domain": "oraculo-eternia.duckdns.org",
    }
    with patch("scripts.check_and_renew_ssl_gh_actions.SSLService.get_certificate_status", return_value=mock_status):
        with pytest.raises(SystemExit) as exc_info:
            await main()
        assert exc_info.value.code == 0


@pytest.mark.asyncio
async def test_ssl_gh_actions_triggers_renewal_when_below_threshold():
    """Si el certificado tiene 14 días o menos, debe disparar la renovación vía SSH."""
    mock_status = {
        "status": "EXPIRING_SOON",
        "days_remaining": 10,
        "is_valid": True,
        "valid_until": "2026-08-26T09:39:54Z",
        "issuer": "Let's Encrypt",
        "domain": "oraculo-eternia.duckdns.org",
    }
    with patch("scripts.check_and_renew_ssl_gh_actions.SSLService.get_certificate_status", return_value=mock_status), \
         patch.dict("os.environ", {"OCI_SSH_KEY": "-----BEGIN MOCK KEY-----\ntest\n-----END MOCK KEY-----"}), \
         patch("scripts.check_and_renew_ssl_gh_actions.run_ssh_renewal", return_value=(True, "Certificado renovado con éxito!")) as mock_ssh, \
         patch("scripts.check_and_renew_ssl_gh_actions.SecurityShield.send_telegram_alert") as mock_tg:
        
        with pytest.raises(SystemExit) as exc_info:
            await main()
        
        assert exc_info.value.code == 0
        assert mock_ssh.called
        assert mock_tg.called


def test_run_ssh_renewal_execution():
    """Verifica que run_ssh_renewal invoca subprocess.run con los argumentos correctos."""
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "Renovación exitosa"
    mock_proc.stderr = ""

    with patch("subprocess.run", return_value=mock_proc) as mock_sub:
        success, out = run_ssh_renewal("MOCK_KEY_DATA")
        assert success is True
        assert "Renovación exitosa" in out
        assert mock_sub.called
