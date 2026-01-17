@echo off
echo ==========================================
echo 🔧 REPARANDO MOTORES DE DOCKER (CACHE)
echo ==========================================
echo.
echo Este script limpiara la cache corrupta de Docker.
echo Una vez terminado, podras volver a lanzar .\launch_ark.ps1
echo.

echo 🧹 1. Limpiando cache de build (BuildKit)...
docker builder prune -a -f

echo.
echo 🧹 2. Limpiando imagenes huerfanas y contenedores...
docker system prune -f

echo.
echo ✅ Limpieza completada.
echo Intenta ejecutar de nuevo: .\launch_ark.ps1
pause
