from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, FloodWait, PeerIdInvalid
import asyncio
from typing import Optional


class GroupManager:
    """Управление группами"""

    def __init__(self, client: Client, logger, action_logger):
        self.client = client
        self.logger = logger
        self.action_logger = action_logger

    async def join_group_and_welcome(self, invite_link: str, welcome_message: str) -> bool:
        """
        Добавление в группу по ссылке и отправка приветствия

        Args:
            invite_link: Ссылка-приглашение (https://t.me/joinchat/...)
            welcome_message: Текст приветствия

        Returns:
            bool: Успех операции
        """
        try:
            # Парсим ссылку
            if "joinchat/" in invite_link:
                hash_part = invite_link.split("joinchat/")[1]
            elif "+" in invite_link:
                hash_part = invite_link.split("+")[1]
            else:
                hash_part = invite_link

            self.logger.info(f"Попытка присоединиться к группе: {invite_link}")

            # Присоединяемся к группе
            try:
                chat = await self.client.join_chat(hash_part)
                self.action_logger.info(f"Добавлен в группу | Ссылка: {invite_link} | Chat ID: {chat.id}")
            except UserAlreadyParticipant:
                # Если уже в группе - получаем информацию
                self.logger.warning(f"Уже состоим в группе: {invite_link}")
                async for dialog in self.client.get_dialogs():
                    if dialog.chat.username and dialog.chat.username in invite_link:
                        chat = dialog.chat
                        break
                else:
                    # Если не нашли по юзернейму, пробуем по ссылке
                    chat = await self.client.get_chat(hash_part)

                self.action_logger.info(f"Уже был в группе | Chat ID: {chat.id}")

            # Отправляем приветствие
            await self._send_welcome(chat.id, welcome_message, is_group=True)

            return True

        except FloodWait as e:
            self.logger.error(f"Флуд-контроль: ждать {e.value} секунд")
            await asyncio.sleep(e.value)
            return await self.join_group_and_welcome(invite_link, welcome_message)

        except PeerIdInvalid as e:
            self.logger.error(f"Неверный ID или ссылка: {e}")
            self.action_logger.error(f"Ошибка добавления в группу | Ссылка: {invite_link} | Ошибка: PeerIdInvalid")
            return False

        except Exception as e:
            self.logger.error(f"Неизвестная ошибка при добавлении в группу: {e}")
            self.action_logger.error(f"Ошибка добавления в группу | Ссылка: {invite_link} | Ошибка: {str(e)}")
            return False

    async def _send_welcome(self, chat_id: int, message: str, is_group: bool = True):
        """Отправка приветствия с обработкой ошибок"""
        try:
            sent_msg = await self.client.send_message(chat_id, message)
            chat_type = "группу" if is_group else "контакт"

            self.logger.info(f"Приветствие отправлено в {chat_type} (ID: {chat_id})")
            self.action_logger.info(
                f"Отправлено приветствие | Тип: {chat_type} | "
                f"Chat ID: {chat_id} | Сообщение: {message[:100]}..."
            )
            return sent_msg

        except Exception as e:
            self.logger.error(f"Ошибка отправки приветствия: {e}")
            self.action_logger.error(f"Ошибка отправки приветствия | Chat ID: {chat_id} | Ошибка: {str(e)}")
            return None