#!/bin/bash
# ============================================================
# 🏰 Oráculo Nueva Eternia — OCI Server Setup Script
# Run this on a fresh Oracle Linux / Ubuntu ARM instance.
# Usage: bash setup_server.sh
# ============================================================

set -e

echo "🏰 ==========================="
echo "   Oráculo: Setup del Servidor"
echo "   Oracle Cloud Infrastructure"
echo "==========================="

# 1. Update system
echo "📦 Paso 1: Actualizando sistema..."
sudo apt-get update && sudo apt-get upgrade -y 2>/dev/null || \
sudo dnf update -y 2>/dev/null

# 2. Install Docker
echo "🐳 Paso 2: Instalando Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker instalado. Necesitarás cerrar sesión y volver a entrar para que el grupo docker surta efecto."
else
    echo "✅ Docker ya está instalado."
fi

# 3. Install Docker Compose (plugin)
echo "🔧 Paso 3: Verificando Docker Compose..."
if ! docker compose version &> /dev/null; then
    sudo apt-get install -y docker-compose-plugin 2>/dev/null || \
    sudo dnf install -y docker-compose-plugin 2>/dev/null
fi
docker compose version

# 4. Enable Docker service
echo "⚡ Paso 4: Habilitando Docker al arranque..."
sudo systemctl enable docker
sudo systemctl start docker

# 5. Install Git
echo "📂 Paso 5: Instalando Git..."
sudo apt-get install -y git 2>/dev/null || sudo dnf install -y git 2>/dev/null

# 6. Clone repository
echo "📥 Paso 6: Clonando repositorio..."
REPO_DIR="$HOME/oraculo-nueva-eternia"
if [ ! -d "$REPO_DIR" ]; then
    git clone https://github.com/DavidLopezGarci4/oraculo-nueva-eternia.git "$REPO_DIR"
    echo "✅ Repositorio clonado en $REPO_DIR"
else
    echo "✅ Repositorio ya existe. Actualizando..."
    cd "$REPO_DIR" && git pull
fi

# 7. Create .env.prod if it doesn't exist
cd "$REPO_DIR"
if [ ! -f ".env.prod" ]; then
    echo "📝 Paso 7: Creando .env.prod (edita con tus credenciales)..."
    cat > .env.prod << 'EOF'
# === Oráculo Nueva Eternia — Production Environment ===
# Base de datos (Supabase Cloud = Nexo Central)
SUPABASE_DATABASE_URL=postgresql://postgres.XXXXXXX:PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
DATABASE_URL=sqlite:///./oraculo.db

# API Key
ORACULO_API_KEY=tu_api_key_aqui

# Telegram Alerts (opcional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Environment
ENV=production
EOF
    echo "⚠️  IMPORTANTE: Edita .env.prod con tus credenciales reales:"
    echo "    nano $REPO_DIR/.env.prod"
else
    echo "✅ .env.prod ya existe."
fi

# 8. Create data directories
echo "📁 Paso 8: Creando directorios de datos..."
mkdir -p data/MOTU/images logs

# 9. Open firewall ports (Oracle Linux / iptables)
echo "🔥 Paso 9: Abriendo puertos del firewall..."
sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || true
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || true
sudo iptables -I INPUT -p tcp --dport 8000 -j ACCEPT 2>/dev/null || true
# Persist iptables rules
sudo sh -c "iptables-save > /etc/iptables/rules.v4" 2>/dev/null || \
sudo netfilter-persistent save 2>/dev/null || true

echo ""
echo "============================================"
echo "🏰 ¡Setup completado!"
echo "============================================"
echo ""
echo "Próximos pasos:"
echo "  1. Edita las credenciales:  nano .env.prod"
echo "  2. Despliega la aplicación: docker compose -f docker-compose.prod.yml up -d --build"
echo "  3. Verifica:                docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "La app estará accesible en: http://<TU_IP_PUBLICA>"
echo ""
