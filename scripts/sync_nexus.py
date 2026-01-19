import asyncio
import sys
import os
from pathlib import Path

# Añadir el root del proyecto al path
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from src.application.services.nexus_service import NexusService
from src.core.logger import setup_logging

async def main():
    setup_logging()
    print("🚀 Lanzando Sincronización del Nexo Maestro (ActionFigure411)...")
    success = await NexusService.sync_catalog()
    if success:
        print("✅ Sincronización completada con éxito.")
    else:
        print("❌ La sincronización falló. Revisa los logs en src/data/logs.")

if __name__ == "__main__":
    asyncio.run(main())
