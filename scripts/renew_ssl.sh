#!/bin/bash
# -----------------------------------------------------------------------------
# 🏰 ORÁCULO DE NUEVA ETERNIA - SSL AUTO RENEWAL & FORCE SCRIPT
# -----------------------------------------------------------------------------
# Se ejecuta a diario a las 03:00 AM (cron) o bajo demanda desde la app/CLI.
# Utiliza el contenedor oficial de Certbot para renovar el certificado SSL.
# Si se renueva (detectado por x509 o salida de Certbot), recarga Nginx y
# notifica con los nuevos datos al Telegram del Administrador.
# -----------------------------------------------------------------------------

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# 1. Detección dinámica del directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 2. Cargar variables de entorno (.env o .env.prod)
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env" 2>/dev/null || true
    set +a
elif [ -f "$PROJECT_DIR/.env.prod" ]; then
    set -a
    source "$PROJECT_DIR/.env.prod" 2>/dev/null || true
    set +a
fi

TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-""}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID:-""}
NGINX_CONTAINER_NAME="oraculo_frontend_prod"
DOMAIN="oraculo-eternia.duckdns.org"
CERT_FILE="$PROJECT_DIR/certbot/conf/live/$DOMAIN/fullchain.pem"

send_telegram_alert() {
    local message="$1"
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=🔒 [Oráculo SSL] $message" \
            -d "parse_mode=HTML" > /dev/null 2>&1 || true
    fi
}

FORCE_FLAG=""
if [ "$1" = "--force" ] || [ "$1" = "-f" ]; then
    FORCE_FLAG="--force-renewal"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚡ Modo de renovación forzada activado (--force-renewal)"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📡 Iniciando comprobación de renovación de certificado SSL para $DOMAIN..."

# Comprobar fecha de vencimiento previa si el archivo existe
EXPIRY_BEFORE=""
if [ -f "$CERT_FILE" ]; then
    EXPIRY_BEFORE=$(openssl x509 -enddate -noout -in "$CERT_FILE" 2>/dev/null | cut -d= -f2)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️ Fecha actual de caducidad: $EXPIRY_BEFORE"
fi

# Ejecutar el contenedor Certbot de Docker
CERTBOT_OUTPUT=$(docker run --rm --name certbot-renew \
  -v "$PROJECT_DIR/certbot/conf:/etc/letsencrypt" \
  -v "$PROJECT_DIR/certbot/www:/var/www/certbot" \
  certbot/certbot renew --webroot -w /var/www/certbot --non-interactive --agree-tos $FORCE_FLAG 2>&1)

CERTBOT_STATUS=$?
echo "$CERTBOT_OUTPUT"

# Comprobar fecha de vencimiento posterior
EXPIRY_AFTER=""
if [ -f "$CERT_FILE" ]; then
    EXPIRY_AFTER=$(openssl x509 -enddate -noout -in "$CERT_FILE" 2>/dev/null | cut -d= -f2)
fi

IS_RENEWED=false
if [ -n "$EXPIRY_AFTER" ] && [ "$EXPIRY_BEFORE" != "$EXPIRY_AFTER" ]; then
    IS_RENEWED=true
elif echo "$CERTBOT_OUTPUT" | grep -qiE "(Congratulations|successfully renewed|Your certificate and chain have been saved)"; then
    IS_RENEWED=true
fi

if [ $CERTBOT_STATUS -eq 0 ]; then
    if [ "$IS_RENEWED" = true ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ ¡Certificado renovado con éxito! Nueva caducidad: $EXPIRY_AFTER"
        
        # Probar y recargar Nginx
        docker exec $NGINX_CONTAINER_NAME nginx -t >/dev/null 2>&1
        RELOAD_OUTPUT=$(docker exec $NGINX_CONTAINER_NAME nginx -s reload 2>&1)
        RELOAD_STATUS=$?
        
        if [ $RELOAD_STATUS -eq 0 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 Nginx recargado con éxito."
            send_telegram_alert "<b>¡Certificado SSL renovado y aplicado!</b>\n\n• Dominio: <code>$DOMAIN</code>\n• Nueva Caducidad: <b>$EXPIRY_AFTER</b>\n• Nginx: Recargado correctamente"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Fallo al recargar Nginx: $RELOAD_OUTPUT"
            send_telegram_alert "<b>Certificado SSL renovado pero falló el reload de Nginx:</b>\n<code>$RELOAD_OUTPUT</code>"
        fi
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 💤 El certificado sigue vigente ($EXPIRY_BEFORE). No se requirió renovación."
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚨 Certbot ha devuelto un error."
    send_telegram_alert "<b>Fallo en el proceso de renovación del certificado SSL</b>\n\nDetalles:\n<code>$CERTBOT_OUTPUT</code>"
    exit 1
fi
