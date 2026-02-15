# 🛡️ Arquitectura Maestra 3OX: El Oráculo de Nueva Eternia
## Guía de Despliegue y Blindaje OCI ( Always Free ARM A1)

Este documento es el manual sagrado para mantener el Oráculo vivo y protegido en la nube de Oracle (OCI).

---

## 🏁 Paso 0: El Túnel de Conexión (SSH)

Antes de cualquier ritual, debes estar dentro del corazón del servidor:
1. Abre tu terminal en Windows (CMD o PowerShell).
2. Conéctate con el comando sagrado:
   ```powershell
   ssh -i "C:\Users\tu-usuario\Documents\Antigravity\oraculo-nueva-eternia\nueva-eternia-produccion.key" opc@79.72.50.244
   ```
   *(Asegúrate de cambiar la ruta de la llave por la real en tu PC).*

---

## 🏗️ Paso 1: Aprovisionamiento y Red (Networking)

Para que el Oráculo sea visible pero seguro, la VCN debe tener estas puertas configuradas en **Ingress Rules**:

| Puerto | Protocolo | Servicio | Estado |
| :--- | :--- | :--- | :--- |
| **80** | TCP | HTTP (Validación Certbot) | ✅ Abierto |
| **443** | TCP | HTTPS (Acceso Seguro) | ✅ Abierto |
| **22** | TCP | SSH (Administración) | ✅ Solo tú |

### Ritual del Firewall Interno (Linux)
Ejecuta esto en tu terminal SSH:
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## 🌐 Paso 2: Dominio y DNS (DuckDNS)

1.  **Subdominio**: `oraculo-eternia.duckdns.org`
2.  **Sincronización**: Configura el cron job:
    ```bash
    crontab -e
    # Pega esto al final:
    */5 * * * * /bin/bash /home/opc/oraculo-nueva-eternia/deploy/duckdns_update.sh
    ```

---

## 🔐 Paso 3: Blindaje SSL (HTTPS)

Usamos **Certbot** vía Docker. **Asegúrate de estar en la carpeta del proyecto**:

```bash
sudo docker run -it --rm --name certbot -v "$(pwd)/certbot/conf:/etc/letsencrypt" -v "$(pwd)/certbot/www:/var/www/certbot" certbot/certbot certonly --webroot -w /var/www/certbot -d oraculo-eternia.duckdns.org
```

---

## 🛠️ Solución de Problemas (Troubleshooting)

### 🔴 Error: "Your local changes would be overwritten by merge"
Si el servidor se niega a actualizarse (git pull), limpia el repositorio con este comando:
```bash
git reset --hard origin/main && git pull origin main
```

### 🔴 Error de Certbot: "Timeout during connect"
1. Verifica que el puerto **80** esté abierto en la consola de Oracle (Security List).
2. Asegúrate de que DuckDNS apunta a la IP correcta (79.72.50.244).

### 🔴 Error de Certbot: "docker run... certbot: error"
**IMPORTANTE**: El comando debe empezar por `sudo docker`. No escribas la palabra `certbot` antes del comando de docker.

---
**Versión**: 1.2.0-FINAL-SHIELD | **Arquitecto**: Antigravity (IA 3OX) | **Estado**: Escudo Máximo Activo
