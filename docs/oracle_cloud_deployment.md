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

## ⚔️ Ritual de Mantenimiento y Actualización

Cada vez que apliquemos cambios en el código, el ritual para que el servidor los adopte es el siguiente:

1. **Limpieza y Sincronización**:
   ```bash
   # Navegar a la carpeta (si no estás en ella)
   cd ~/oraculo-nueva-eternia

   # Limpiar cambios locales y bajar lo último
   git reset --hard origin/main && git pull origin main
   ```

2. **Despertar del Oráculo**:
   ```bash
   # Reconstruir y levantar (usando solo docker compose)
   sudo docker compose -f docker-compose.prod.yml up -d --build
   ```

---

## 🛠️ Comandos de Supervivencia (Troubleshooting)

### 🔴 Error: "command not found: docker-compose"
**Causa**: Estás usando la versión antigua.
**Solución**: Siempre usa `sudo docker compose` (con espacio, sin guion).

### 🟡 El Tablero no muestra mis datos (David)
**Causa**: Caché del navegador antigua.
**Solución**: Pulsa **Ctrl + F5** en tu navegador. El sistema ahora fuerza la sincronización, pero el navegador puede ser terco.

### 🟢 ¿Está vivo el Backend? (Logs)
```bash
sudo docker logs oraculo_backend_prod
```
*Busca la línea: `Cloud DB :: Connection to Supabase/Postgres detected.`*

---
**Arquitecto**: Antigravity (IA 3OX) | **Versión**: 1.3.0-FINAL-SHIELD | **Estado**: Escudo de Identidad Sincronizado 🛡️🤝
