from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message

from db import Database
from settings import MEDIA_ROOT


class EventHandlers:
    """Обработчики событий от пользователей"""

    def __init__(self, db: Database, client: Client, logger, action_logger):
        self.db = db
        self.client = client
        self.logger = logger
        self.action_logger = action_logger
        self._register_handlers()

    def _register_handlers(self):
        """Регистрация всех обработчиков"""

        @self.client.on_message(filters.private & filters.text)
        async def handle_private_message(client: Client, message: Message):
            """Обработка личных сообщений к боту"""

            user = message.from_user
            log_entry = (
                f"Сообщение от пользователя | "
                f"ID: {user.id} | Имя: {user.first_name} | "
                f"Username: @{user.username} | "
                f"Текст: {message.text[:200]}"
            )
            self.action_logger.info(log_entry)
            self.logger.info(f"Получено сообщение от {user.first_name}: {message.text[:50]}...")

            # Здесь можно добавить логику ответа на сообщения
            # Например: команды /help, /status и т.д.
            if message.text.lower() == '/start':
                await message.reply(
                    "👋 Привет! Я Userbot.\n\n"
                    "Мои команды:\n"
                    "/status - статус бота\n"
                    "/help - эта справка"
                )
                self.action_logger.info(f"Отправлен ответ /start пользователю {user.id}")

            elif message.text.lower() == '/status':
                me = await client.get_me()
                status = (
                    f"✅ Бот активен\n"
                    f"📱 Аккаунт: {me.first_name}\n"
                    f"🆔 ID: {me.id}\n"
                    f"👥 В контактах: (информация о контактах)"
                )
                await message.reply(status)
                self.action_logger.info(f"Отправлен статус пользователю {user.id}")

        @self.client.on_message(filters.group & filters.text)
        async def handle_group_message(client: Client, message: Message):
            """Обработка сообщений в группах (просто логируем)"""

            chat = message.chat
            user = message.from_user

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
                    self.logger.error(f"Failed to download media for message {tg_msg_id}: {e}")

            raw_json = message.__dict__ if hasattr(message, '__dict__') else {}

            try:
                await self.db.save_message(
                    tg_msg_id, chat_id, chat_name, timestamp, text, media_paths, raw_json
                )
                await self.db.update_status(True, timestamp)
                self.logger.info(f"Saved message {tg_msg_id} from {chat_name}")
            except Exception as e:
                self.logger.error(f"Failed to save message {tg_msg_id}: {e}")

            self.action_logger.info(
                f"Сообщение в группе | Группа: {chat.title} (ID: {chat.id}) | "
                f"Пользователь: {user.first_name} (ID: {user.id}) | "
                f"Текст: {message.text[:200]}"
            )