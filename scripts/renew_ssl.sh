#!/bin/bash
# -----------------------------------------------------------------------------
# 🏰 ORÁCULO DE NUEVA ETERNIA - SSL AUTO RENEWAL & FORCE SCRIPT (HYBRID V2)
# -----------------------------------------------------------------------------
# Funciona de forma resiliente tanto en el host (Linux/OCI) como dentro del
# contenedor Docker del backend. Soporta ejecución directa de Certbot o
# invocación a través del daemon de Docker.
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

# Detectar rutas de certificados en host o contenedor
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    CONF_DIR="/etc/letsencrypt"
    WWW_DIR="/var/www/certbot"
elif [ -d "$PROJECT_DIR/certbot/conf" ]; then
    CONF_DIR="$PROJECT_DIR/certbot/conf"
    WWW_DIR="$PROJECT_DIR/certbot/www"
elif [ -d "/app/certbot/conf" ]; then
    CONF_DIR="/app/certbot/conf"
    WWW_DIR="/app/certbot/www"
else
    CONF_DIR="/etc/letsencrypt"
    WWW_DIR="/var/www/certbot"
fi

# 3. Auto-enlace y consistencia para el entorno de contenedor
if [ "$CONF_DIR" != "/etc/letsencrypt" ] && [ -d "$CONF_DIR" ]; then
    if [ ! -e "/etc/letsencrypt" ]; then
        mkdir -p /etc 2>/dev/null || true
        ln -sfn "$CONF_DIR" /etc/letsencrypt 2>/dev/null || true
    fi
    if [ ! -e "/var/www/certbot" ] && [ -d "$WWW_DIR" ]; then
        mkdir -p /var/www 2>/dev/null || true
        ln -sfn "$WWW_DIR" /var/www/certbot 2>/dev/null || true
    fi
fi

# 4. Auto-reparación de symlinks de Certbot (si los archivos live fueron copiados como ficheros regulares)
for TARGET_DIR in "$CONF_DIR" "/etc/letsencrypt"; do
    LIVE_DIR="$TARGET_DIR/live/$DOMAIN"
    ARCHIVE_DIR="$TARGET_DIR/archive/$DOMAIN"
    if [ -d "$LIVE_DIR" ] && [ -d "$ARCHIVE_DIR" ]; then
        for item in cert privkey chain fullchain; do
            FILE_PATH="$LIVE_DIR/$item.pem"
            if [ -f "$FILE_PATH" ] && [ ! -L "$FILE_PATH" ]; then
                LATEST_ARCHIVE=$(ls -1 "$ARCHIVE_DIR/${item}"*.pem 2>/dev/null | sort -V | tail -n 1)
                if [ -n "$LATEST_ARCHIVE" ]; then
                    ARCHIVE_FILENAME=$(basename "$LATEST_ARCHIVE")
                    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔧 Auto-reparando symlink de Certbot: $item.pem -> ../../archive/$DOMAIN/$ARCHIVE_FILENAME"
                    rm -f "$FILE_PATH"
                    ln -s "../../archive/$DOMAIN/$ARCHIVE_FILENAME" "$FILE_PATH"
                fi
            fi
        done
    fi
done

CERT_FILE="$CONF_DIR/live/$DOMAIN/fullchain.pem"
if [ ! -f "$CERT_FILE" ] && [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    CERT_FILE="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
fi

WORK_DIR="/tmp/certbot-work"
LOGS_DIR="/tmp/certbot-logs"
mkdir -p "$WORK_DIR" "$LOGS_DIR" "$WWW_DIR" 2>/dev/null || true

send_telegram_alert() {
    local message="$1"
    local keyboard='{"inline_keyboard":[[{"text":"🔄 Forzar Renovación SSL","callback_data":"ssl:renew"},{"text":"📊 Estado SSL","callback_data":"ssl:status"}]]}'
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=🔒 [Oráculo SSL] $message" \
            -d "parse_mode=HTML" \
            -d "reply_markup=$keyboard" > /dev/null 2>&1 || true
    fi
}

FORCE_FLAG=""
if [ "$1" = "--force" ] || [ "$1" = "-f" ]; then
    FORCE_FLAG="--force-renewal"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚡ Modo de renovación forzada activado (--force-renewal)"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📡 Iniciando comprobación de renovación SSL para $DOMAIN..."

# Comprobar fecha de vencimiento previa
EXPIRY_BEFORE=""
if [ -f "$CERT_FILE" ]; then
    EXPIRY_BEFORE=$(openssl x509 -enddate -noout -in "$CERT_FILE" 2>/dev/null | cut -d= -f2)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️ Fecha actual de caducidad: $EXPIRY_BEFORE"
fi

CERTBOT_OUTPUT=""
CERTBOT_STATUS=1

# Estrategia 1: Certbot binario directo (nativo en host o instalado en contenedor)
if command -v certbot >/dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚙️ Ejecutando Certbot directo en el entorno..."
    
    # Determinar si usamos /etc/letsencrypt o CONF_DIR
    ACTIVE_CONF="$CONF_DIR"
    ACTIVE_WWW="$WWW_DIR"
    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        ACTIVE_CONF="/etc/letsencrypt"
        ACTIVE_WWW="/var/www/certbot"
    fi

    CERTBOT_OUTPUT=$(certbot renew \
        --webroot \
        -w "$ACTIVE_WWW" \
        --config-dir "$ACTIVE_CONF" \
        --work-dir "$WORK_DIR" \
        --logs-dir "$LOGS_DIR" \
        --non-interactive \
        --agree-tos \
        $FORCE_FLAG 2>&1)
    CERTBOT_STATUS=$?

# Estrategia 2: Contenedor Docker de Certbot (si docker está disponible)
elif command -v docker >/dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🐳 Ejecutando Certbot mediante contenedor Docker..."
    CERTBOT_OUTPUT=$(docker run --rm --name certbot-renew \
      -v "$CONF_DIR:/etc/letsencrypt" \
      -v "$WWW_DIR:/var/www/certbot" \
      certbot/certbot renew --webroot -w /var/www/certbot --non-interactive --agree-tos $FORCE_FLAG 2>&1)
    CERTBOT_STATUS=$?
else
    CERTBOT_OUTPUT="Error: No se encontró ni el binario 'certbot' ni 'docker' en el sistema."
    CERTBOT_STATUS=127
fi

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
        if command -v docker >/dev/null 2>&1; then
            docker exec $NGINX_CONTAINER_NAME nginx -t >/dev/null 2>&1
            RELOAD_OUTPUT=$(docker exec $NGINX_CONTAINER_NAME nginx -s reload 2>&1)
            RELOAD_STATUS=$?
            if [ $RELOAD_STATUS -eq 0 ]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 Nginx recargado con éxito."
                send_telegram_alert "<b>¡Certificado SSL renovado y aplicado!</b>\n\n• Dominio: <code>$DOMAIN</code>\n• Nueva Caducidad: <b>$EXPIRY_AFTER</b>\n• Nginx: Recargado correctamente"
            else
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ Certificado renovado pero falló el reload de Nginx: $RELOAD_OUTPUT"
                send_telegram_alert "<b>Certificado SSL renovado pero falló reload de Nginx:</b>\n<code>$RELOAD_OUTPUT</code>"
            fi
        elif command -v nginx >/dev/null 2>&1; then
            nginx -s reload 2>/dev/null || true
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 Nginx recargado directamente en el host."
            send_telegram_alert "<b>¡Certificado SSL renovado con éxito!</b>\n\n• Dominio: <code>$DOMAIN</code>\n• Nueva Caducidad: <b>$EXPIRY_AFTER</b>"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️ Certificado renovado en disco."
            send_telegram_alert "<b>¡Certificado SSL renovado con éxito!</b>\n\n• Dominio: <code>$DOMAIN</code>\n• Nueva Caducidad: <b>$EXPIRY_AFTER</b>"
        fi
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 💤 El certificado sigue vigente ($EXPIRY_BEFORE). No se requirió renovación."
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚨 Certbot ha devuelto un error."
    send_telegram_alert "<b>Fallo en el proceso de renovación del certificado SSL</b>\n\nDetalles:\n<code>$CERTBOT_OUTPUT</code>"
    exit 1
fi
