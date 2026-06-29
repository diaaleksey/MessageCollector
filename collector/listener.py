import asyncio
import logging
from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pathlib import Path
from typing import List, Dict

from settings import TG_API_ID, TG_API_HASH, TG_PHONE_NUMBER, MEDIA_ROOT
from db import Database

logger = logging.getLogger(__name__)

class TelegramListener:
    def __init__(self, db: Database, chats: List[Dict]):
        self.db = db
        self.chats = chats
        self.client = Client(
            "my_account",
            api_id=TG_API_ID,
            api_hash=TG_API_HASH,
            phone_number=TG_PHONE_NUMBER,
            workdir="."
        )
        self.running = False
        self.connected = False

    async def start(self):
        logger.info("Starting Telegram listener...")
        self.running = True
        delay = 1
        max_delay = 60

        while self.running:
            try:
                await self.client.start()
                self.connected = True
                await self.db.update_status(True, None)
                logger.info("Telegram client started successfully")

                # Обработчик сообщений
                self.client.add_handler(MessageHandler(self.handle_message))

                # Присоединение к чатам по invite-ссылкам (если указаны)
                for chat in self.chats:
                    identifier = chat.get("identifier")
                    if isinstance(identifier, str) and (
                        identifier.startswith("https://t.me/joinchat/") or
                        identifier.startswith("https://t.me/+") or
                        identifier.startswith("+") or
                        identifier.startswith("joinchat")
                    ):
                        try:
                            await self.client.join_chat(identifier)
                            logger.info(f"Joined chat via invite link: {identifier}")
                        except Exception as e:
                            logger.error(f"Failed to join chat {identifier}: {e}")

                # Ждём, пока клиент не отключится
                await self.client.idle()

                # Если дошли сюда, клиент отключился
                self.connected = False
                await self.db.update_status(False, None)
                logger.warning("Telegram client disconnected. Reconnecting...")

            except Exception as e:
                logger.error(f"Telegram client error: {e}")
                self.connected = False
                await self.db.update_status(False, None)
                logger.info(f"Reconnecting in {delay} seconds...")
                await asyncio.sleep(delay)
                delay = min(delay * 2, max_delay)

            if not self.running:
                break

    async def stop(self):
        self.running = False
        if self.client:
            await self.client.stop()
        self.connected = False
        await self.db.update_status(False, None)

    async def handle_message(self, client, message):
        # Проверяем, принадлежит ли чат целевому списку
        chat_id = str(message.chat.id)
        target_ids = [str(chat.get("identifier")) for chat in self.chats if chat.get("identifier")]
        target_usernames = [chat.get("username") for chat in self.chats if chat.get("username")]

        if chat_id not in target_ids:
            if message.chat.username and message.chat.username in target_usernames:
                pass
            else:
                return

        logger.debug(f"Received message from {message.chat.title or message.chat.id}")

        tg_msg_id = message.id
        chat_id = str(message.chat.id)
        chat_name = message.chat.title or "Unknown"
        timestamp = message.date
        text = message.text or message.caption or ""

        media_paths = []
        if message.media:
            media_dir = Path(MEDIA_ROOT) / chat_id
            media_dir.mkdir(parents=True, exist_ok=True)
            file_name = f"{tg_msg_id}_{message.media.value}"
            try:
                downloaded = await client.download_media(message, file_name=str(media_dir / file_name))
                if downloaded:
                    rel_path = str(Path(MEDIA_ROOT) / chat_id / file_name)
                    media_paths.append(rel_path)
            except Exception as e:
                logger.error(f"Failed to download media for message {tg_msg_id}: {e}")

        raw_json = message.__dict__ if hasattr(message, '__dict__') else {}

        try:
            await self.db.save_message(
                tg_msg_id, chat_id, chat_name, timestamp, text, media_paths, raw_json
            )
            await self.db.update_status(True, timestamp)
            logger.info(f"Saved message {tg_msg_id} from {chat_name}")
        except Exception as e:
            logger.error(f"Failed to save message {tg_msg_id}: {e}")