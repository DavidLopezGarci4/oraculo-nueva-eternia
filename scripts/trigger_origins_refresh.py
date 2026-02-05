
import asyncio
import logging
import sys
from src.application.services.nexus_service import NexusService

# Force logging to console for visibility
logging.basicConfig(level=logging.INFO)

async def run_nuclear_sync():
    print("STARTING NUCLEAR SYNC: PURGING ALL PRODUCTS AND RE-SCRAPING ORIGINS...")
    try:
        success = await NexusService.sync_catalog(purge_before_sync=True)
        if success:
            print("SUCCESS: NUCLEAR SYNC COMPLETED SUCCESSFULLY!")
        else:
            print("FAILURE: NUCLEAR SYNC FAILED. Check logs for details.")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_nuclear_sync())
