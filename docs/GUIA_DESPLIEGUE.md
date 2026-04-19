# 🚀 Guía de Despliegue: El Oráculo de Nueva Eternia

Referencia rápida para actualizar y poner en marcha la aplicación de forma segura, tanto en local como en producción (OCI / DuckDNS).

---

## 🗺️ Arquitectura de Entornos

| Entorno | Comando Docker | Frontend | Backend | URL |
| :--- | :--- | :--- | :--- | :--- |
| **Local Dev** | `docker-compose.yml` | Puerto 3001 | Puerto 8000 | `http://localhost:3001` |
| **Local Prod** | `docker-compose.local-prod.yml` | Puerto 80/443 | Puerto 8000 | `http://localhost` |
| **Producción** | `docker-compose.local-prod.yml` (en OCI) | Puerto 80/443 | Puerto 8000 | `https://oraculo-eternia.duckdns.org` |

---

## 🔄 Flujo Completo: Desde un PR hasta Producción

### Paso 1 — Revisar y mergear el PR

Cuando Claude Code crea cambios, los sube a una rama `claude/...` y abre un PR en GitHub.

1. Abre el PR en GitHub → revisa los cambios (diff).
2. Si todo es correcto → **"Merge pull request"** → **"Confirm merge"**.
3. Borra la rama del PR (botón "Delete branch" que aparece tras el merge).

> ⚠️ Nunca hagas push directo a `main`. Siempre vía PR para tener trazabilidad.

---

### Paso 2 — Actualizar tu máquina local

```powershell
cd C:\Users\dace8\OneDrive\Documentos\Antigravity\oraculo-nueva-eternia

# Traer los cambios mergeados
git pull origin main

# Verificar que estás en main y al día
git status
git log --oneline -3
```

---

### Paso 3 — Cerrar lo que usa los puertos (CRÍTICO)

**El error más común**: `bind: Solo se permite un uso de cada dirección de socket`

Antes de arrancar Docker, **mata cualquier proceso que ocupe los puertos 3001, 8000, 80 o 443**.

```powershell
# Ver qué ocupa el puerto (ejemplo: 3001)
netstat -ano | findstr ":3001"
# Anota el PID de la columna de la derecha

# Matar el proceso por PID (reemplaza 304 con el tuyo)
Stop-Process -Id 304 -Force

# Alternativa: matar todos los procesos Node.js (si era npm run dev)
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue

# Verificar que el puerto quedó libre
netstat -ano | findstr ":3001"
# No debe mostrar nada
```

**Causa típica del conflicto en puerto 3001**: el servidor de desarrollo del frontend (`npm run dev`) estaba corriendo. Siempre ciérralo antes de levantar Docker.

---

### Paso 4 — Arrancar Docker en local

```powershell
# Modo desarrollo (hot-reload, puerto 3001)
.\launch_ark.ps1

# --- O manualmente ---
docker-compose down --remove-orphans
docker-compose up --build
```

Señales de éxito en los logs:
```
✔ Container oraculo_backend   Started
✔ Container oraculo_frontend  Started
INFO: Application startup complete.
```

Abre `http://localhost:3001` para verificar.

---

### Paso 5 — Desplegar en Producción (OCI / DuckDNS)

La producción corre en el servidor Oracle Cloud (ARM A1). El flujo es:

#### 5a. Conectar al servidor OCI

```powershell
# (Ajusta usuario e IP según tu configuración OCI)
ssh ubuntu@<IP-OCI-SERVER>
# O si usas clave SSH:
ssh -i ~/.ssh/oraculo_key ubuntu@<IP-OCI-SERVER>
```

#### 5b. Actualizar el código en el servidor

```bash
cd ~/oraculo-nueva-eternia   # ruta del proyecto en OCI

# Traer los últimos cambios de main
git pull origin main

# Verificar qué cambió
git log --oneline -3
```

#### 5c. Reconstruir y reiniciar los contenedores

```bash
# Parar contenedores actuales SIN borrar volúmenes (preserva datos)
docker-compose -f docker-compose.local-prod.yml down --remove-orphans

# Reconstruir imágenes e iniciar
docker-compose -f docker-compose.local-prod.yml up --build -d

# Verificar que todo arrancó
docker ps
docker logs oraculo_backend_prod --tail 30
```

> La flag `-d` (detached) es esencial en producción — los contenedores quedan corriendo en segundo plano tras cerrar la sesión SSH.

#### 5d. Verificar en producción

```bash
# Estado de los contenedores
docker ps

# Logs en vivo (Ctrl+C para salir)
docker logs -f oraculo_backend_prod

# Test rápido de API
curl -s http://localhost:8000/health | python3 -m json.tool
```

Abre `https://oraculo-eternia.duckdns.org` en el navegador.

---

## ⚡ Cheatsheet de Comandos Docker

```powershell
# Arrancar (construyendo imágenes si hay cambios)
docker-compose up --build

# Arrancar en segundo plano
docker-compose up --build -d

# Parar todo (preserva volúmenes/datos)
docker-compose down

# Parar y borrar volúmenes (¡DESTRUCTIVO! Solo para reset total)
docker-compose down -v

# Ver contenedores activos
docker ps

# Ver logs de un contenedor
docker logs oraculo_backend --tail 50 -f

# Entrar a un contenedor en ejecución
docker exec -it oraculo_backend bash

# Ver uso de recursos
docker stats
```

---

## 🐛 Problemas Frecuentes y Soluciones

### Error: `bind: Solo se permite un uso de cada dirección de socket`
**Causa**: Otro proceso (Node.js, Python, Nginx local) ocupa el puerto.  
**Solución**: Ver Paso 3 arriba. Mata el proceso conflictivo y reintenta.

### Error: `container name already in use`
**Causa**: Un contenedor anterior con el mismo nombre no fue eliminado.  
**Solución**:
```powershell
docker rm -f oraculo_backend oraculo_frontend
docker-compose up --build
```

### El frontend carga pero la API da 502/504
**Causa**: El backend no arrancó correctamente.  
**Solución**:
```powershell
docker logs oraculo_backend --tail 50
# Revisar el error. Típicamente: variable de entorno faltante o error de importación Python.
```

### Los cambios de código no se reflejan
**Causa**: La imagen Docker tiene caché del código anterior.  
**Solución**: Forzar rebuild sin caché:
```powershell
docker-compose build --no-cache
docker-compose up
```

### GitHub Actions no ejecuta los scrapers
**Causa**: El workflow solo corre en `main`. Si los cambios están en un branch sin mergear, no se ejecutan.  
**Solución**: Mergear el PR a `main` (ver Paso 1).

---

## 📋 Checklist de Despliegue Seguro

Antes de hacer merge y desplegar, confirma:

- [ ] El PR tiene los cambios esperados (revisar diff en GitHub)
- [ ] No hay errores en los logs del CI de GitHub Actions
- [ ] Los archivos `.env` / secretos **no** están incluidos en el commit
- [ ] Si añadiste un scraper nuevo: está registrado en `daily_scan.py` Y en `main.py` (3 puntos)
- [ ] Si eliminaste un scraper: eliminado en todos los puntos de registro
- [ ] `docker-compose down` ejecutado antes de `up` para evitar contenedores huérfanos
- [ ] Puertos 3001/8000 libres antes de `docker-compose up`

---

## 🔁 Ciclo GitHub Actions (Automático)

Los scrapers se ejecutan **automáticamente** sin intervención manual:

| Hora UTC | Hora España (verano) | Acción |
| :--- | :--- | :--- |
| 02:00 UTC | 04:00 CEST | Escaneo nocturno completo |
| 14:30 UTC | 16:30 CEST | Escaneo vespertino completo |

Para lanzar manualmente:
1. GitHub → **Actions** → **Oracle Master Workflow (Daily Scan)**
2. **Run workflow** → introduce tiendas específicas (opcional) → **Run workflow**

---

> **Regla de oro**: `git pull` → matar puertos → `docker-compose up --build`. En ese orden, siempre.
