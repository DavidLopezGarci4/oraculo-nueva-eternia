import html
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.core.config import settings
from loguru import logger
import secrets

class EmailService:
    @staticmethod
    def send_reset_email(to_email: str, username: str, token: str):
        """
        Envía un correo de recuperación de contraseña.
        """
        if not settings.SMTP_USER or not settings.SMTP_PASS:
            logger.warning(f"📧 SMTP NOT CONFIGURED. Reset email skipped for {to_email} (token redacted).")
            return False

        # El enlace apuntará al frontend (dominio de OCI)
        # TODO: Hacer que la URL base sea configurable si el puerto cambia
        reset_link = f"https://oraculo-eternia.duckdns.org/#/reset-password?token={token}"

        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM
        msg['To'] = to_email
        msg['Subject'] = "🔑 Recuperación de Eternia: Reseteo de Llave"

        body = f"""
        Hola {username},
        
        Se ha solicitado una nueva llave para entrar al Oráculo de Nueva Eternia.
        Haz clic en el siguiente enlace para resetear tu contraseña (vence en 1 hora):
        
        {reset_link}
        
        Si no has solicitado esto, puedes ignorar este mensaje.
        
        --- 
        3OX Shield Persistence
        """
        
        safe_username = html.escape(str(username or "Guardián"))
        # Versión HTML opcional (puedes mejorarla después)
        html_body = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #00bcd4;">Recuperación de Eternia</h2>
            <p>Hola <strong>{safe_username}</strong>,</p>
            <p>Se ha solicitado un reseteo de contraseña para tu cuenta en el Oráculo.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" style="background-color: #00bcd4; color: black; padding: 15px 25px; text-decoration: none; font-weight: bold; border-radius: 5px;">RESETEAR MI CONTRASEÑA</a>
            </div>
            <p style="font-size: 12px; color: #666;">Este enlace caducará en 1 hora. Si no solicitaste este cambio, ignora este correo.</p>
            <hr />
            <p style="font-size: 10px; color: #999;">3OX Shield :: Oráculo de Nueva Eternia</p>
        </div>
        """

        msg.attach(MIMEText(body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        try:
            logger.info(f"📧 Intentando enviar email a {to_email} vía {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.set_debuglevel(1) if settings.DEBUG else None
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg)
            logger.info(f"✅ Email de reseteo enviado satisfactoriamente a {to_email}")
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error(f"❌ Error de Autenticación SMTP: Verifica el SMTP_PASS (Contraseña de Aplicación).")
            return False
        except smtplib.SMTPConnectError:
            logger.error(f"❌ Error de Conexión SMTP: No se pudo alcanzar {settings.SMTP_HOST}.")
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado al enviar email: {type(e).__name__}: {e}")
            return False
