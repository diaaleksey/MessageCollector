import os
from operator import concat

from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Dict

load_dotenv()

# БД
DATABASE_URL = os.getenv("DATABASE_URL")

# Базовые пути
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
SESSIONS_DIR = BASE_DIR / "sessions"

CHATS_FILE = "chats.json"
MEDIA_ROOT = "media"
LOG_FILE = LOGS_DIR / "collector.log"


# Создаем директории если их нет
LOGS_DIR.mkdir(exist_ok=True)
SESSIONS_DIR.mkdir(exist_ok=True)

# Telegram Auth
TG_API_ID = int(os.getenv("TG_API_ID"))
TG_API_HASH = os.getenv("TG_API_HASH")
TG_PHONE_NUMBER = os.getenv("TG_PHONE_NUMBER")
TG_PHONE_CODE = os.getenv("TG_PHONE_CODE")
TG_PASSWORD = os.getenv("TG_PASSWORD")
# Настройки Userbot
USERBOT_NAME = "myUserBot"
# SESSION_NAME = str(SESSIONS_DIR / "userbot_session")
SESSION_NAME = concat(USERBOT_NAME,"_session")
# Настройки MTProto Proxy
# Формат MTProto: "host:port" или с параметрами: "host:port:secret"
MT_PROXY_HOST = os.getenv("MT_PROXY_HOST", "")
MT_PROXY_PORT = int(os.getenv("MT_PROXY_PORT", 0)) if os.getenv("MT_PROXY_PORT") else None
MT_PROXY_SECRET = os.getenv("MT_PROXY_SECRET", "")  # Если есть secret (hex или строка)

# Автоматическая сборка конфига прокси
proxy_config: Optional[Dict] = None
if MT_PROXY_HOST and MT_PROXY_PORT:
    proxy_config = {
        "scheme": "mtproto",  # или "socks4", "socks5"
        "hostname": MT_PROXY_HOST,
        "port": MT_PROXY_PORT
    }

    # Добавляем secret если есть
    if MT_PROXY_SECRET:
        proxy_config["secret"] = MT_PROXY_SECRET

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Поддержка нескольких прокси для ротации
PROXY_LIST = []  # Можно добавить список прокси для ротации


