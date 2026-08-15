# 🏰 Guía de Despliegue: Oráculo en Oracle Cloud

Guía paso a paso para desplegar el Oráculo en OCI Always Free.

## Paso 1: Crear la Red (VCN)

1. Ve a la consola de Oracle Cloud: [cloud.oracle.com](https://cloud.oracle.com)
2. Menú ☰ → **Networking** → **Virtual Cloud Networks**
3. Click **"Start VCN Wizard"** → **"Create VCN with Internet Connectivity"**
4. Nombre: `eternia-vcn`
5. Click **"Create"** → Espera a que termine → **"View VCN"**

### Abrir puertos (Security List)
1. Dentro de la VCN, click en **"Public Subnet-eternia-vcn"**
2. Click en la **Security List** que aparece
3. Click **"Add Ingress Rules"** y añade estas reglas:

| Source CIDR | Protocol | Port Range | Descripción |
|---|---|---|---|
| `0.0.0.0/0` | TCP | 80 | HTTP (Frontend) |
| `0.0.0.0/0` | TCP | 443 | HTTPS (futuro) |
| `0.0.0.0/0` | TCP | 8000 | API Backend |

## Paso 2: Crear la Instancia de Compute

1. Menú ☰ → **Compute** → **Instances**
2. Click **"Create Instance"**
3. Configuración:
   - **Name**: `oraculo-eternia`
   - **Image**: **Oracle Linux 9** o **Ubuntu 22.04** (Canonical)
   - **Shape**: Click "Change Shape"
     - **Ampere** → `VM.Standard.A1.Flex`
     - **OCPUs**: `4` (o menos si quieres dejar margen)
     - **Memory**: `24 GB` (o el máximo gratis que permita)
   - **Networking**: Selecciona `eternia-vcn` y la **subred pública**
   - **SSH Key**: 
     - Si ya tienes una key SSH: sube tu `.pub`
     - Si no: selecciona **"Generate a key pair"** y **descarga ambos archivos** (los necesitarás)
4. Click **"Create"** → Espera ~2 min

> [!IMPORTANT]
> **Guarda la IP Pública** que aparece una vez creada la instancia. La necesitarás para conectarte.

## Paso 3: Conectar por SSH

Desde tu terminal de Windows (PowerShell):

```powershell
# Si descargaste la key de OCI:
ssh -i C:\Users\dace8\Downloads\ssh-key-*.key opc@<TU_IP_PUBLICA>

# Si usas Ubuntu como imagen:
ssh -i C:\Users\dace8\Downloads\ssh-key-*.key ubuntu@<TU_IP_PUBLICA>
```

> [!TIP]
> Si te da error de permisos en la key, ejecuta desde PowerShell:
> ```powershell
> icacls "C:\Users\dace8\Downloads\ssh-key-*.key" /inheritance:r /grant:r "$env:USERNAME:(R)"
> ```

## Paso 4: Setup automático del servidor

Ya dentro del servidor (SSH), ejecuta:

```bash
# Descargar y ejecutar el setup
curl -fsSL https://raw.githubusercontent.com/DavidLopezGarci4/oraculo-nueva-eternia/main/deploy/setup_server.sh | bash
```

O si prefieres hacerlo manualmente:
```bash
# Clonar repositorio
git clone https://github.com/DavidLopezGarci4/oraculo-nueva-eternia.git
cd oraculo-nueva-eternia

# Ejecutar setup
bash deploy/setup_server.sh
```

## Paso 5: Configurar credenciales

```bash
cd ~/oraculo-nueva-eternia
nano .env.prod
```

Rellena con tus credenciales reales de Supabase:
```env
SUPABASE_DATABASE_URL=postgresql://postgres.XXXXXXX:TU_PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
ORACULO_API_KEY=tu_api_key
```

## Paso 6: Desplegar 🚀

```bash
cd ~/oraculo-nueva-eternia

# Build y arranque
docker compose -f docker-compose.prod.yml up -d --build

# Verificar que los contenedores están corriendo
docker compose -f docker-compose.prod.yml ps

# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml logs -f
```

## Paso 7: Verificar

Abre tu navegador y ve a:
```
http://<TU_IP_PUBLICA>
```

¡Deberías ver el Oráculo! 🏰

## Comandos útiles

```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs -f backend

# Reiniciar
docker compose -f docker-compose.prod.yml restart

# Actualizar código
cd ~/oraculo-nueva-eternia
git pull
docker compose -f docker-compose.prod.yml up -d --build

# Parar todo
docker compose -f docker-compose.prod.yml down

# Forzar renovación manual de Certificados SSL (Let's Encrypt)
bash scripts/renew_ssl.sh --force

# Comprobar tareas programadas de renovación SSL y DuckDNS
crontab -l
```

## 🔒 Certificados SSL (Let's Encrypt / HTTPS)

El Oráculo renueva automáticamente sus certificados a diario a las 03:00 AM. Si tus certificados caducaron o necesitas regenerarlos de inmediato:

1. **Desde la Aplicación**: Ve a **Configuración > Ajustes > Escudo de Encriptación SSL** y pulsa **"Forzar Renovación de Certificados"**.
2. **Desde la Terminal SSH**:
```bash
cd ~/oraculo-nueva-eternia
bash scripts/renew_ssl.sh --force
```

