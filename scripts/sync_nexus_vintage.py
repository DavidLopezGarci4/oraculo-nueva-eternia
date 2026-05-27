import asyncio
import sys
import os
from pathlib import Path

# Añadir el root del proyecto al path
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from src.application.services.nexus_vintage_service import NexusVintageService
from src.core.logger import setup_logging

async def main():
    setup_logging()
    print("🚀 Lanzando Sincronización del Nexo Maestro Vintage (ActionFigure411)...")
    success = await NexusVintageService.sync_catalog()
    if success:
        print("✅ Sincronización Vintage completada con éxito.")
    else:
        print("❌ La sincronización Vintage falló. Revisa los logs en src/data/logs o la tabla de telemetría.")

if __name__ == "__main__":
    asyncio.run(main())
