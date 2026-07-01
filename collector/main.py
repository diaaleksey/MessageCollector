import asyncio

from message_collector import MessageCollector
from contact_manager import ContactManager
from group_manager import GroupManager
from handlers import EventHandlers
from logger import setup_logger
from settings import DATABASE_URL, USERBOT_NAME
from db import Database

# Настройка логирования
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.StreamHandler(sys.stdout),
#         logging.FileHandler(LOG_FILE)
#     ]
# )
# logger = logging.getLogger(__name__)
logger, action_logger = setup_logger("UserBot.Main")
async def main():
    # chats_path = Path(CHATS_FILE)
    # if not chats_path.exists():
    #     logger.error(f"Chats file {CHATS_FILE} not found")
    #     return

    # with open(chats_path, 'r') as f:
    #     chats = json.load(f)
    # Инициализация БД
    db = Database(DATABASE_URL)

    # Инициализация бота
    message_collector = MessageCollector(USERBOT_NAME)

    try:
        bot_client = await message_collector.initialize()
        # Запускаем с автоматическими переподключениями
        if not await message_collector.start_with_retry(max_retries=3):
            logger.error("❌ Не удалось запустить бота после всех попыток")
            return

        # Инициализация БД
        await db.init()
        logger.info("Database initialized")

        # Инициализация менеджеров
        group_manager = GroupManager(bot_client, logger, action_logger)
        contact_manager = ContactManager(bot_client, logger, action_logger)

        # Инициализация обработчиков событий
        event_handlers = EventHandlers(db, bot_client, logger, action_logger)



        # ✅ ТВОИ ЗАДАНИЯ ДЛЯ ВЫПОЛНЕНИЯ
        # Раскомментируй нужные строки и укажи параметры

        # 1. Добавление в группу и приветствие
        # await group_manager.join_group_and_welcome(
        #     invite_link="https://t.me/+xxxxxxxxxxx",
        #     welcome_message="👋 Привет всем! Я новый участник. Рад быть с вами!"
        # )

        # 2. Добавление контакта и приветствие
        # await contact_manager.add_contact_and_welcome(
        #     user_input="@username",
        #     welcome_message="Привет, {name}! Рад познакомиться!"
        # )

        logger.info("🚀 Userbot запущен и готов к работе")
        logger.info("📝 Все действия логируются в папке logs/")
        logger.info("⏸ Для остановки нажми Ctrl+C")
        # Держим бота активным
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Received stop signal")
    finally:
        # await listener.stop()
        if message_collector:
            await message_collector.stop()
        if db:
            await db.close()

        logger.info("Shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())