@echo off
echo ============================================================
echo    WALLAPOP MANUAL IMPORTER - EL ORACULO DE ETERNIA
echo ============================================================
echo.
echo Este script te permite importar datos de Wallapop manualmente.
echo.
echo PASOS:
echo 1. Abre Wallapop en tu navegador
echo 2. Busca "motu origins" o el termino que desees
echo 3. Copia los datos en formato: Nombre ^| Precio ^| URL
echo 4. Pega aqui y escribe FIN cuando termines
echo.
echo ============================================================
cd /d "%~dp0"
set PYTHONPATH=.
python src\infrastructure\scrapers\wallapop_manual_importer.py
pause
