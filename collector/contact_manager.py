from pyrogram import Client
from pyrogram.errors import FloodWait, PeerIdInvalid
import asyncio
from typing import Union


class ContactManager:
    """Управление контактами"""

    def __init__(self, client: Client, logger, action_logger):
        self.client = client
        self.logger = logger
        self.action_logger = action_logger

    async def add_contact_and_welcome(self, user_input: Union[str, int], welcome_message: str) -> bool:
        """
        Добавление контакта и отправка приветствия

        Args:
            user_input: Имя пользователя (@username), номер телефона или ID
            welcome_message: Текст приветствия

        Returns:
            bool: Успех операции
        """
        try:
            # Получаем информацию о пользователе
            user = await self._resolve_user(user_input)

            if not user:
                self.logger.error(f"Не удалось найти пользователя: {user_input}")
                self.action_logger.error(f"Ошибка поиска контакта | Входные данные: {user_input}")
                return False

            # Добавляем в контакты
            try:
                await self.client.add_contact(
                    user_id=user.id,
                    first_name=user.first_name or "User",
                    last_name=user.last_name or ""
                )
                self.logger.info(f"Добавлен контакт: {user.first_name} (@{user.username})")
                self.action_logger.info(
                    f"Добавлен контакт | ID: {user.id} | "
                    f"Имя: {user.first_name} | Username: @{user.username}"
                )

            except Exception as e:
                self.logger.warning(f"Не удалось добавить в контакты (возможно уже есть): {e}")

            # Отправляем приветствие
            await self._send_welcome(user.id, welcome_message, user.first_name)

            return True

        except FloodWait as e:
            self.logger.error(f"Флуд-контроль: ждать {e.value} секунд")
            await asyncio.sleep(e.value)
            return await self.add_contact_and_welcome(user_input, welcome_message)

        except PeerIdInvalid as e:
            self.logger.error(f"Неверный ID пользователя: {e}")
            self.action_logger.error(
                f"Ошибка добавления контакта | Входные данные: {user_input} | Ошибка: PeerIdInvalid")
            return False

        except Exception as e:
            self.logger.error(f"Неизвестная ошибка при добавлении контакта: {e}")
            self.action_logger.error(f"Ошибка добавления контакта | Входные данные: {user_input} | Ошибка: {str(e)}")
            return False

    async def _resolve_user(self, user_input: Union[str, int]):
        """Поиск пользователя по разным идентификаторам"""
        try:
            # Если это число - вероятно ID
            if isinstance(user_input, int) or user_input.isdigit():
                return await self.client.get_users(int(user_input))

            # Если начинается с @ - username
            elif user_input.startswith('@'):
                return await self.client.get_users(user_input)

            # Иначе пробуем как номер телефона или другую строку
            else:
                return await self.client.get_users(user_input)

        except Exception as e:
            self.logger.error(f"Не удалось найти пользователя {user_input}: {e}")
            return None

    async def _send_welcome(self, user_id: int, message: str, user_name: str = "User"):
        """Отправка персонализированного приветствия"""
        try:
            # Можно добавить персонализацию
            personalized_message = message.replace("{name}", user_name)

            sent_msg = await self.client.send_message(user_id, personalized_message)

            self.logger.info(f"Приветствие отправлено пользователю {user_name} (ID: {user_id})")
            self.action_logger.info(
                f"Отправлено приветствие | Пользователь: {user_name} | "
                f"ID: {user_id} | Сообщение: {personalized_message[:100]}..."
            )
            return sent_msg

        except Exception as e:
            self.logger.error(f"Ошибка отправки приветствия пользователю {user_id}: {e}")
            self.action_logger.error(f"Ошибка отправки приветствия | Пользователь ID: {user_id} | Ошибка: {str(e)}")
            return None