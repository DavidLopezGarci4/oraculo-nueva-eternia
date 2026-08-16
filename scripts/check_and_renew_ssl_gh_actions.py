"""
Script de comprobación y renovación automática de certificados SSL para GitHub Actions.
--------------------------------------------------------------------------------------
Este script se ejecuta de forma programada en CI/CD (GitHub Actions) y comprueba la
vigencia TLS del dominio en vivo (oraculo-eternia.duckdns.org).

- Si faltan MÁS de 14 días: Finaliza inmediatamente en verde con 0 consumo de cómputo.
- Si faltan 14 DÍAS O MENOS: Conecta vía SSH al servidor de Oracle Cloud y ejecuta
  el script oficial `bash ~/oraculo-nueva-eternia/scripts/renew_ssl.sh --force`,
  recargando Nginx y enviando un reporte completo a Telegram.
"""
from __future__ import annotations

import os
import ssl
import sys
import socket
import tempfile
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Añadir raíz del proyecto al path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.application.services.ssl_service import SSLService
from src.core.security import SecurityShield

RENEWAL_THRESHOLD_DAYS = 14
TARGET_DOMAIN = "oraculo-eternia.duckdns.org"
TARGET_PORT = 443
SSH_USER = os.environ.get("OCI_SSH_USER", "opc")
SSH_HOST = os.environ.get("OCI_SSH_HOST", "79.72.50.244")


def run_ssh_renewal(private_key_content: str) -> tuple[bool, str]:
    """Ejecuta la renovación remota de SSL en Oracle Cloud vía SSH."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".key") as tmp_key:
        tmp_key.write(private_key_content.strip() + "\n")
        tmp_key_path = tmp_key.name

    try:
        if os.name != "nt":
            os.chmod(tmp_key_path, 0o600)

        remote_cmd = "cd ~/oraculo-nueva-eternia && bash scripts/renew_ssl.sh --force"
        ssh_cmd = [
            "ssh",
            "-i", tmp_key_path,
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ConnectTimeout=20",
            f"{SSH_USER}@{SSH_HOST}",
            remote_cmd,
        ]

        print(f"📡 Conectando por SSH a {SSH_USER}@{SSH_HOST} para renovar SSL...")
        res = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=240)
        output = (res.stdout + "\n" + res.stderr).strip()
        success = res.returncode == 0
        return success, output
    except Exception as e:
        return False, f"Excepción durante conexión SSH: {e}"
    finally:
        try:
            os.unlink(tmp_key_path)
        except Exception:
            pass


async def main():
    print("=" * 70)
    print("🛡️ ORÁCULO DE NUEVA ETERNIA - GUARDIÁN SSL (CI/CD)")
    print("=" * 70)
    print(f"Dominio objetivo: {TARGET_DOMAIN}:{TARGET_PORT}")
    print(f"Umbral de renovación preventiva: {RENEWAL_THRESHOLD_DAYS} días")

    # 1. Inspección TLS en vivo
    status = SSLService.get_certificate_status()
    days_remaining = status.get("days_remaining", 0)
    is_valid = status.get("is_valid", False)
    valid_until = status.get("valid_until")

    print(f"• Estado actual: {status.get('status')}")
    print(f"• Días restantes: {days_remaining} días")
    print(f"• Válido hasta: {valid_until}")
    print(f"• Emisor: {status.get('issuer')}")

    # 2. Comprobación de umbral
    if is_valid and days_remaining > RENEWAL_THRESHOLD_DAYS:
        print(f"\n✅ Certificado SSL en estado óptimo ({days_remaining} días restantes > {RENEWAL_THRESHOLD_DAYS} días).")
        print("No se requiere acción de renovación.")
        sys.exit(0)

    # 3. Alerta y ejecución si faltan <= 14 días
    print(f"\n⚠️ ¡ATENCIÓN! Quedan {days_remaining} días (<= {RENEWAL_THRESHOLD_DAYS} días). Iniciando protocolo de renovación preventiva...")

    ssh_key = (
        os.environ.get("OCI_SSH_KEY")
        or os.environ.get("SSH_PRIVATE_KEY")
        or os.environ.get("SSH_KEY")
    )

    if ssh_key:
        success, details = run_ssh_renewal(ssh_key)
        print("\n--- DETALLE DE EJECUCIÓN REMOTA ---")
        print(details)
        print("----------------------------------")

        if success:
            print("\n🎉 ¡Certificados SSL renovados con éxito en Oracle Cloud!")
            msg = (
                "🔒 <b>[GitHub Actions] Renovación Preventiva de SSL Exitosa</b>\n\n"
                f"• Dominio: <code>{TARGET_DOMAIN}</code>\n"
                f"• Motivo: <i>Quedaban {days_remaining} días (umbral ≤ 14 días)</i>\n"
                "• Estado: <b>Renovado y Nginx recargado con éxito</b>\n\n"
                "✨ <i>Los certificados de producción han sido ampliados por otros 90 días.</i>"
            )
            await SecurityShield.send_telegram_alert(msg)
            sys.exit(0)
        else:
            print(f"\n❌ Error al ejecutar renovación remota por SSH.")
            err_msg = (
                "🚨 <b>[GitHub Actions] Fallo en la Renovación Preventiva de SSL</b>\n\n"
                f"• Dominio: <code>{TARGET_DOMAIN}</code>\n"
                f"• Días Restantes: <b>{days_remaining} días</b>\n"
                f"• Error: <code>{details[:300]}</code>\n\n"
                "⚠️ <i>Ejecuta la opción [11] en oraculo.ps1 desde tu ordenador para renovarlo manualmente.</i>"
            )
            await SecurityShield.send_telegram_alert(err_msg)
            sys.exit(1)
    else:
        print("⚠️ No se encontró la clave SSH (OCI_SSH_KEY / SSH_PRIVATE_KEY) en las variables de entorno.")
        alert_msg = (
            "⚠️ <b>[Guardián SSL] Alerta Preventiva de Caducidad</b>\n\n"
            f"• Dominio: <code>{TARGET_DOMAIN}</code>\n"
            f"• Días Restantes: <b>{days_remaining} días</b> (≤ 14 días para expirar)\n\n"
            "🔔 <i>Por favor, ejecuta la opción [11] de <code>oraculo.ps1</code> desde tu PC o pulsa Renovar en la web.</i>"
        )
        await SecurityShield.send_telegram_alert(alert_msg)
        sys.exit(0)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
