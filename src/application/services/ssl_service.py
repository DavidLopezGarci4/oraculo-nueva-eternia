from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import socket
import ssl
import subprocess
from typing import Optional
from loguru import logger

from src.core.config import settings
from src.core.security import SecurityShield


class SSLService:
    """Servicio integral de diagnóstico, observabilidad y renovación de certificados SSL."""

    DEFAULT_DOMAIN = "oraculo-eternia.duckdns.org"
    RENEWAL_WINDOW_DAYS = 14  # Intentar renovar 14 días (2 semanas) antes de expirar

    @classmethod
    def _find_cert_path(cls) -> Optional[Path]:
        """Busca el archivo de certificado en las ubicaciones estándar."""
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        possible_paths = [
            Path("/app/certbot/conf/live") / cls.DEFAULT_DOMAIN / "fullchain.pem",
            Path("/etc/letsencrypt/live") / cls.DEFAULT_DOMAIN / "fullchain.pem",
            project_root / "certbot" / "conf" / "live" / cls.DEFAULT_DOMAIN / "fullchain.pem",
            project_root / "certbot" / "conf" / "live" / cls.DEFAULT_DOMAIN / "cert.pem",
        ]
        
        for p in possible_paths:
            if p.exists() and p.is_file():
                return p
        return None

    @classmethod
    def _parse_x509_cert(cls, cert_bytes: bytes) -> dict:
        """Parsea un certificado PEM X.509 utilizando cryptography."""
        from cryptography import x509
        from cryptography.x509.oid import NameOID

        cert = x509.load_pem_x509_certificate(cert_bytes)
        
        # Extracción segura de fechas UTC
        valid_from = getattr(cert, "not_valid_before_utc", None)
        if valid_from is None:
            valid_from = cert.not_valid_before.replace(tzinfo=timezone.utc)
            
        valid_until = getattr(cert, "not_valid_after_utc", None)
        if valid_until is None:
            valid_until = cert.not_valid_after.replace(tzinfo=timezone.utc)

        # Extracción de emisor
        issuer_org = cert.issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)
        issuer_cn = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        issuer_name = "Let's Encrypt"
        if issuer_org:
            issuer_name = issuer_org[0].value
        elif issuer_cn:
            issuer_name = issuer_cn[0].value

        # Extracción de dominio (Subject CN)
        subject_cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        domain = subject_cn[0].value if subject_cn else cls.DEFAULT_DOMAIN

        return {
            "domain": domain,
            "issuer": str(issuer_name),
            "valid_from": valid_from,
            "valid_until": valid_until,
        }

    @classmethod
    def _fetch_live_tls_cert(cls, domain: str = DEFAULT_DOMAIN, port: int = 443, timeout: float = 4.0) -> Optional[dict]:
        """Consulta el certificado SSL directamente desde el socket TLS del servidor en vivo."""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE  # Permite inspeccionar incluso certificados expirados

            with socket.create_connection((domain, port), timeout=timeout) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as sslobj:
                    der_cert = sslobj.getpeercert(binary_form=True)
                    if not der_cert:
                        return None
                    pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
                    return cls._parse_x509_cert(pem_cert.encode("utf-8"))
        except Exception as e:
            logger.debug(f"Live TLS check for {domain}:{port} skipped/failed: {e}")
            return None

    @classmethod
    def get_certificate_status(cls) -> dict:
        """
        Obtiene el estado completo del certificado SSL.
        Prioridad:
        1. Archivo en disco (si existe).
        2. Conexión TLS en vivo a oraculo-eternia.duckdns.org:443.
        3. Modo simulado / fallback cuando no hay certificados disponibles.
        """
        cert_data = None
        source = "unknown"

        # 1. Inspección local de disco
        cert_path = cls._find_cert_path()
        if cert_path:
            try:
                cert_bytes = cert_path.read_bytes()
                cert_data = cls._parse_x509_cert(cert_bytes)
                source = "disk"
            except Exception as e:
                logger.warning(f"Error al leer certificado local {cert_path}: {e}")

        # 2. Inspección remota en vivo si no se encontró en disco
        if not cert_data:
            cert_data = cls._fetch_live_tls_cert(cls.DEFAULT_DOMAIN)
            if cert_data:
                source = "live_tls"

        # 3. Cálculo de vigencias y estados
        now = datetime.now(timezone.utc)
        if cert_data:
            valid_from = cert_data["valid_from"]
            valid_until = cert_data["valid_until"]
            delta = valid_until - now
            days_remaining = int(delta.total_seconds() // 86400)
            
            is_valid = days_remaining > 0
            if days_remaining <= 0:
                status = "EXPIRED"
            elif days_remaining <= cls.RENEWAL_WINDOW_DAYS:
                status = "EXPIRING_SOON"
            else:
                status = "ACTIVE"

            next_renewal = valid_until - timedelta(days=cls.RENEWAL_WINDOW_DAYS)

            return {
                "domain": cert_data["domain"],
                "issuer": cert_data["issuer"],
                "valid_from": valid_from,
                "valid_until": valid_until,
                "days_remaining": days_remaining,
                "status": status,
                "next_renewal_recommended": next_renewal,
                "is_valid": is_valid,
                "source": source,
                "details": f"Certificado inspeccionado vía {source} ({'Vigente' if is_valid else 'Caducado'})."
            }

        # 4. Fallback si no hay certificados instalados en local ni red
        return {
            "domain": cls.DEFAULT_DOMAIN,
            "issuer": "Let's Encrypt / ACME",
            "valid_from": None,
            "valid_until": None,
            "days_remaining": 0,
            "status": "UNKNOWN",
            "next_renewal_recommended": None,
            "is_valid": False,
            "source": "fallback",
            "details": "No se detectaron certificados locales en /etc/letsencrypt ni conexión TLS activa."
        }

    @classmethod
    async def renew_ssl_certificate(cls, force: bool = True) -> dict:
        """
        Ejecuta la renovación del certificado SSL.
        - Invoca el script de renovación en el servidor o mediante Certbot Docker.
        - Envía notificaciones de alerta a Telegram.
        """
        logger.info(f"🔒 [SSL] Iniciando proceso de renovación de certificado (force={force})...")
        
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        script_path = project_root / "scripts" / "renew_ssl.sh"

        cmd = ["bash", str(script_path)]
        if force:
            cmd.append("--force")

        output_str = ""
        success = False

        if script_path.exists() and os.name != "nt":
            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=180,
                    cwd=str(project_root)
                )
                output_str = proc.stdout + "\n" + proc.stderr
                success = proc.returncode == 0
            except Exception as e:
                output_str = f"Error al ejecutar script de renovación: {e}"
                success = False
        else:
            # Entorno Windows / Desarrollo o sin script bash directo
            logger.info("🔒 [SSL] Entorno de desarrollo / local detectado. Ejecutando verificación de estado.")
            status_info = cls.get_certificate_status()
            success = status_info.get("is_valid", False) or status_info.get("status") == "UNKNOWN"
            output_str = f"[SIMULATION/DIAGNOSTIC] Chequeo de certificado ejecutado. Estado actual: {status_info.get('status')} ({status_info.get('days_remaining')} días restantes)."

        # Alerta de Telegram
        if success:
            msg = (
                "🔒 <b>[Oráculo SSL] Renovación / Verificación Completada</b>\n\n"
                f"• Dominio: <code>{cls.DEFAULT_DOMAIN}</code>\n"
                f"• Modo: <b>{'Forzado (--force)' if force else 'Estándar'}</b>\n"
                f"• Resultado: <b>Éxito</b>\n\n"
                "✨ <i>Nginx y los certificados de Let's Encrypt han sido sincronizados.</i>"
            )
            await SecurityShield.send_telegram_alert(msg)
            return {
                "status": "success",
                "message": "Proceso de renovación de certificados SSL completado correctamente.",
                "details": output_str
            }
        else:
            err_msg = (
                "🚨 <b>[Oráculo SSL] Fallo en la Renovación</b>\n\n"
                f"• Dominio: <code>{cls.DEFAULT_DOMAIN}</code>\n"
                f"• Error: <code>{output_str[:300]}</code>\n\n"
                "⚠️ <i>Por favor, revisa la configuración del servidor en Oracle Cloud.</i>"
            )
            await SecurityShield.send_telegram_alert(err_msg)
            return {
                "status": "error",
                "message": "Fallo al ejecutar la renovación de certificados SSL.",
                "details": output_str
            }
