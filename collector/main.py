import asyncio
import logging
import sys
import json
from pathlib import Path

from settings import DATABASE_URL, CHATS_FILE, LOG_FILE
from db import Database
from listener import TelegramListener

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE)
    ]
)
logger = logging.getLogger(__name__)

async def main():
    chats_path = Path(CHATS_FILE)
    if not chats_path.exists():
        logger.error(f"Chats file {CHATS_FILE} not found")
        return

    with open(chats_path, 'r') as f:
        chats = json.load(f)

    db = Database(DATABASE_URL)
    await db.init()
    logger.info("Database initialized")

    listener = TelegramListener(db, chats)
    try:
        await listener.start()
    except KeyboardInterrupt:
        logger.info("Received stop signal")
    finally:
        await listener.stop()
        await db.close()
        logger.info("Shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())