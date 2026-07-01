import logging
from logging.handlers import RotatingFileHandler
from settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT
from colorama import init, Fore, Style
import sys

init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Форматтер с цветным выводом в консоль"""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        log_message = super().format(record)
        if record.levelname in self.COLORS:
            return f"{self.COLORS[record.levelname]}{log_message}{Style.RESET_ALL}"
        return log_message


def setup_logger(name: str = "UserBot") -> logging.Logger:
    """Настройка и возврат логгера с несколькими обработчиками"""

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Обработчик для файла (ротация каждые 5 МБ)
    file_handler = RotatingFileHandler(
        LOGS_DIR / "userbot.log",
        maxBytes=5_000_000,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    logger.addHandler(file_handler)

    # Отдельный файл для действий бота (бизнес-логи)
    action_handler = RotatingFileHandler(
        LOGS_DIR / "actions.log",
        maxBytes=5_000_000,
        backupCount=3,
        encoding='utf-8'
    )
    action_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s', LOG_DATE_FORMAT))

    # Создаем отдельный логгер для действий
    action_logger = logging.getLogger(f"{name}.actions")
    action_logger.setLevel(logging.INFO)
    action_logger.addHandler(action_handler)

    # Консольный обработчик с цветами
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(LOG_FORMAT, LOG_DATE_FORMAT))
    logger.addHandler(console_handler)

    return logger, action_logger