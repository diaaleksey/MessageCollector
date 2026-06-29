import os
from dotenv import load_dotenv

load_dotenv()

TG_API_ID = int(os.getenv("TG_API_ID"))
TG_API_HASH = os.getenv("TG_API_HASH")
TG_PHONE_NUMBER = os.getenv("TG_PHONE_NUMBER")
DATABASE_URL = os.getenv("DATABASE_URL")
CHATS_FILE = "chats.json"
MEDIA_ROOT = "media"
LOG_FILE = "logs/collector.log"