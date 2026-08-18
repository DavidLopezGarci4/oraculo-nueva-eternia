import asyncio
import argparse
import sys
import logging
from pathlib import Path

# Setup root path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.application.services.vinted_hunter_service import VintedHunterService

logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description="Vinted Hunter Script")
    parser.add_argument("--query", type=str, default="auto", help="Search query or 'auto'")
    parser.add_argument("--chat-id", type=str, default=None, help="Telegram Chat ID for notifications")
    args = parser.parse_args()

    print(f"🏹 Starting Vinted Hunter with query='{args.query}'...")
    res = await VintedHunterService.run_hunt(query=args.query, chat_id=args.chat_id)
    print(f"🏹 Hunter Finished. Result: {res}")

if __name__ == "__main__":
    asyncio.run(main())
