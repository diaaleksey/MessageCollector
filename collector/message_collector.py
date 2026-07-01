from pyrogram import Client
from settings import (
    TG_API_ID, TG_API_HASH, SESSION_NAME, MT_PROXY_HOST, TG_PHONE_NUMBER,
    SESSIONS_DIR, TG_PHONE_CODE, TG_PASSWORD
 )
from logger import setup_logger
from typing import Optional
import asyncio


class MessageCollector:
    """Класс для управления клиентом Userbot с поддержкой прокси"""

    def __init__(self, client_name: str = "UserBot.Client"):
        """
        Args:
            use_proxy: Использовать прокси из конфига
            proxy_rotation: Использовать ротацию прокси (если несколько)
        """
        self.logger, self.action_logger = setup_logger(client_name)
        self.client: Optional[Client] = None
        # self.use_proxy = use_proxy
        # self.proxy_rotation = proxy_rotation
        self.current_proxy = None
        self.is_running = False  # Флаг состояния клиента

    # def _get_proxy_config(self) -> Optional[dict]:
    #     """Получение конфигурации прокси"""
    #
    #     if not self.use_proxy:
    #         return None
    #
    #     # Если есть ротация и список прокси
    #     if self.proxy_rotation and PROXY_LIST:
    #         self.current_proxy = random.choice(PROXY_LIST)
    #         self.logger.info(f"Выбран прокси для ротации: {self.current_proxy.get('hostname')}")
    #         return self.current_proxy
    #
    #     # Используем прокси из конфига
    #     if proxy_config:
    #         self.logger.info(f"Используем MTProto прокси: {MT_PROXY_HOST}:{MT_PROXY_PORT}")
    #         return proxy_config
    #
    #     self.logger.warning("Прокси не найден в конфигурации")
    #     return None

    async def initialize(self) -> Client:
        """Инициализация клиента с прокси"""
        try:
            proxy = None  # self._get_proxy_config()

            # Создаем клиент с прокси
            self.client = Client(
                name=SESSION_NAME,
                api_id=TG_API_ID,
                api_hash=TG_API_HASH,
                phone_number=TG_PHONE_NUMBER,
                # phone_code=TG_PHONE_CODE,
                # password=TG_PASSWORD,
                # proxy=proxy,  # Добавляем прокси
                workdir=SESSIONS_DIR,
                # Дополнительные настройки для стабильности
                sleep_threshold=30,  # Таймаут при проблемах с сетью
                no_updates=False,  # Получаем обновления
                takeout=False

                # Важно: добавляем таймауты для соединения
                # timeout=15
            )

            if proxy:
                self.logger.info(f"Клиент инициализирован с прокси: {proxy.get('hostname')}:{proxy.get('port')}")
            else:
                self.logger.info("Клиент инициализирован без прокси (прямое подключение)")

            return self.client

        except Exception as e:
            self.logger.error(f"Ошибка инициализации клиента: {e}")
            raise

    async def start(self) -> bool:
        """Запуск клиента с проверкой прокси"""
        if self.client is None:
            self.logger.error("Клиент не инициализирован")
            return False

        try:
            # Пробуем подключиться через прокси
            await self.client.start()
            self.is_running = True

            # Проверяем, что прокси работает (если используется)
            if self.use_proxy:
                try:
                    me = await self.client.get_me()
                    self.logger.info(f"✅ Прокси работает корректно. Подключен как {me.first_name}")
                except Exception as e:
                    self.logger.error(f"❌ Прокси не работает или заблокирован: {e}")
                    await self.stop()  # Чистое завершение
                    return False

            # Получаем информацию о пользователе
            me = await self.client.get_me()
            self.logger.info(f"✅ Запущен как {me.first_name} (@{me.username})")

            self.action_logger.info(
                f"Бот запущен | User: {me.first_name} (@{me.username}) | ID: {me.id} | "
                f"Proxy: {MT_PROXY_HOST if self.use_proxy else 'No'}"
            )
            return True

        except ConnectionError as e:
            self.logger.error(f"Ошибка подключения: {e}")
            await self.stop()
            return False
        except Exception as e:
            self.logger.error(f"Ошибка запуска: {e}")
            await self.stop()
            return False

    async def start_with_retry(self, max_retries: int = 3) -> bool:
        """Запуск с автоматическим переподключением при ошибках"""

        for attempt in range(max_retries):
            try:
                if self.client is None:
                    await self.initialize()

                if attempt > 0:
                    self.logger.info(f"Попытка переподключения #{attempt + 1}")
                    # Пересоздаем клиент при повторе
                    if self.client:
                        await self.stop()
                    await self.initialize()

                # Пробуем запустить
                if await self.start():
                    return True
                else:
                    self.logger.warning(f"Попытка {attempt + 1} не удалась")

            except ConnectionError as e:
                self.logger.error(f"Ошибка соединения (попытка {attempt + 1}): {e}")

                if attempt < max_retries - 1:
                    # Проверяем прокси перед повтором
                    self.logger.info(f"Повтор через {5 * (attempt + 1)} секунд...")
                    await asyncio.sleep(5 * (attempt + 1))
                else:
                    self.logger.error("❌ Не удалось подключиться после всех попыток")
                    return False

            except Exception as e:
                self.logger.error(f"Неизвестная ошибка в попытке {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(3)
                else:
                    return False

        return False

    async def stop(self):
        """Безопасная остановка клиента"""
        if not self.is_running:
            self.logger.debug("Клиент уже остановлен или не был запущен")
            return

        try:
            if self.client and self.is_running:
                self.logger.info("Останавливаем клиент...")
                await self.client.stop()
                self.is_running = False
                self.logger.info("Бот остановлен")
                self.action_logger.info("Бот остановлен")
        except ConnectionError as e:
            # Игнорируем ошибку "Client is already terminated"
            if "already terminated" in str(e):
                self.logger.debug("Клиент уже был завершен")
            else:
                self.logger.error(f"Ошибка при остановке: {e}")
        except Exception as e:
            self.logger.error(f"Неизвестная ошибка при остановке: {e}")
        finally:
            self.is_running = False
            self.client = None  # Сбрасываем клиент

    # async def rotate_proxy(self) -> bool:
    #     """Ротация прокси (переподключение с новым прокси)"""
    #     if not self.proxy_rotation or not PROXY_LIST:
    #         self.logger.warning("Ротация прокси не настроена")
    #         return False
    #
    #     try:
    #         # Останавливаем текущее соединение
    #         await self.stop()
    #
    #         # Выбираем новый прокси
    #         old_proxy = self.current_proxy
    #         self.current_proxy = random.choice([p for p in PROXY_LIST if p != old_proxy])
    #
    #         # Создаем новый клиент с новым прокси
    #         self.client = Client(
    #             name=SESSION_NAME,
    #             api_id=API_ID,
    #             api_hash=API_HASH,
    #             proxy=self.current_proxy,
    #             workdir=".",
    #             timeout=15
    #         )
    #
    #         # Перезапускаем
    #         await self.client.start()
    #         self.is_running = True
    #
    #         self.logger.info(f"Прокси сменен: {old_proxy.get('hostname')} -> {self.current_proxy.get('hostname')}")
    #         self.action_logger.info(f"Смена прокси | Новый: {self.current_proxy.get('hostname')}")
    #
    #         return True
    #
    #     except Exception as e:
    #         self.logger.error(f"Ошибка ротации прокси: {e}")
    #         return False