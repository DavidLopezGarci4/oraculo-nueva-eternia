import asyncio
from src.application.services.nexus_service import NexusService
import logging

logging.basicConfig(level=logging.INFO)

async def trigger_nexus():
    print("--- DISPARANDO NEXO MAESTRO (RE-INTELLIGENCE) ---")
    success = await NexusService.sync_catalog()
    if success:
        print("--- NEXO SINCRONIZADO CON EXITO ---")
    else:
        print("--- FALLO EN EL NEXO ---")

if __name__ == "__main__":
    asyncio.run(trigger_nexus())
