#!/bin/bash
# -----------------------------------------------------------------------------
# ORÁCULO DE NUEVA ETERNIA - SSL AUTO RENEWAL SCRIPT
# -----------------------------------------------------------------------------
# Se ejecuta a diario a las 03:00 AM.
# Utiliza el contenedor oficial de Certbot para renovar el certificado SSL.
# Si tiene éxito y se renueva, recarga Nginx y sale.
# Si falla, envía una alerta al Telegram del Administrador.
# -----------------------------------------------------------------------------

# Cargar variables de entorno del proyecto
PROJECT_DIR="/home/opc/oraculo-nueva-eternia"
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

# Variables por defecto
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-""}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID:-""}
NGINX_CONTAINER_NAME="oraculo_frontend_prod"

send_telegram_alert() {
    local message="$1"
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=🚨 [Oráculo SSL] $message" \
            -d "parse_mode=Markdown" > /dev/null
    fi
}

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📡 Iniciando comprobación de renovación de certificado SSL..."

# Ejecutar el contenedor Certbot de Docker
# Se mapean los directorios de let's encrypt locales y la ruta de webroot compartida con Nginx
CERTBOT_OUTPUT=$(docker run --rm --name certbot-renew \
  -v "$PROJECT_DIR/certbot/conf:/etc/letsencrypt" \
  -v "$PROJECT_DIR/certbot/www:/var/www/certbot" \
  certbot/certbot renew --webroot -w /var/www/certbot --non-interactive --agree-tos 2>&1)

CERTBOT_STATUS=$?

echo "$CERTBOT_OUTPUT"

if [ $CERTBOT_STATUS -eq 0 ]; then
    # Certbot se ejecutó correctamente. Verificamos si realmente se renovó un certificado
    if echo "$CERTBOT_OUTPUT" | grep -q "Congratulations"; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Certificado renovado con éxito! Recargando Nginx..."
        
        # Recargar Nginx para aplicar el nuevo certificado
        RELOAD_OUTPUT=$(docker exec $NGINX_CONTAINER_NAME nginx -s reload 2>&1)
        if [ $? -eq 0 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 Nginx recargado con éxito."
            send_telegram_alert "¡El certificado SSL ha sido renovado y aplicado con éxito en el servidor!"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Fallo al recargar Nginx: $RELOAD_OUTPUT"
            send_telegram_alert "Certificado SSL renovado pero falló la recarga de Nginx: $RELOAD_OUTPUT"
        fi
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 💤 El certificado aún está vigente. No se requiere renovación."
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚨 Certbot ha devuelto un error."
    send_telegram_alert "Fallo en el proceso de renovación automática del certificado SSL. Detalles:\n\`\`\`\n$CERTBOT_OUTPUT\n\`\`\`"
fi
