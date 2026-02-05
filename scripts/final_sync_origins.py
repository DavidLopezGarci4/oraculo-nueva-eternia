
import asyncio
import logging
import sys
from src.application.services.nexus_service import NexusService

# Force logging to console for visibility
logging.basicConfig(level=logging.INFO)

async def run_final_sync():
    print("STARTING FINAL INCREMENTAL SYNC: PUSHING 'ADQUIRIDO' STATUS TO DB...")
    try:
        # purge_before_sync=False ensures we don't wipe the data we just scraped
        success = await NexusService.sync_catalog(purge_before_sync=False)
        if success:
            print("SUCCESS: FINAL SYNC COMPLETED SUCCESSFULLY!")
        else:
            print("FAILURE: FINAL SYNC FAILED. Check logs for details.")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_final_sync())
