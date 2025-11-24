# src/utils/logger.py
import logging

# from logging.handlers import RotatingFileHandler # Removed: No longer needed for file logging

# --- 1. DEFINE CUSTOM LOG LEVELS (FAILED, SUCCEED) ---
FAILED_LEVEL_NUM = 45
logging.addLevelName(FAILED_LEVEL_NUM, "FAILED")

SUCCEED_LEVEL_NUM = 35  # Between INFO (30) and WARNING (40)
logging.addLevelName(SUCCEED_LEVEL_NUM, "SUCCEED")


def failed(self, message, *args, **kws):
    """Log a message with FAILED level."""
    if self.isEnabledFor(FAILED_LEVEL_NUM):
        self._log(FAILED_LEVEL_NUM, message, args, **kws)


def succeed(self, message, *args, **kws):
    """Log a message with SUCCEED level."""
    if self.isEnabledFor(SUCCEED_LEVEL_NUM):
        self._log(SUCCEED_LEVEL_NUM, message, args, **kws)


# Assign utility functions to the Logger class
logging.Logger.failed = failed
logging.Logger.succeed = succeed
# ----------------------------------------------------


class ColorFormatter(logging.Formatter):
    """
    Custom Formatter to add color to log messages in the console.
    """

    COLORS = {
        logging.ERROR: "\033[91m",  # Red
        logging.INFO: "\033[92m",  # Green
        SUCCEED_LEVEL_NUM: "\033[96m",  # Cyan for SUCCEED
        logging.WARNING: "\033[93m",  # Yellow
        logging.DEBUG: "\033[94m",  # Blue
        FAILED_LEVEL_NUM: "\033[95m",  # Purple for FAILED
        logging.CRITICAL: "\033[41m\033[97m",  # White text on Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


# Class TaskIDFormatFilter is removed.


class Logger:
    """
    Singleton class to manage and configure a custom logger (Console-only).
    """

    _instances = {}

    # Removed: RESULT_LOG_FILE

    def __new__(cls, name: str = "app_logger", level=logging.DEBUG):
        if name not in cls._instances:
            instance = super(Logger, cls).__new__(cls)
            logger = logging.getLogger(name)

            if not logger.handlers:
                # Removed: logger.addFilter(TaskIDFormatFilter())

                # 1. Stream Handler (Console/Terminal)
                stream_handler = logging.StreamHandler()

                # Formatter updated: Removed %(task_id_formatted)s
                formatter = ColorFormatter("%(levelname)s [%(name)s]: %(message)s")
                stream_handler.setFormatter(formatter)
                logger.addHandler(stream_handler)

                # 2. File Handler logic removed (Rotating log file)

                # Set the logger's main level
                logger.setLevel(level)

            cls._instances[name] = logger

        return cls._instances[name]
