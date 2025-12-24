import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Buat folder logs jika belum ada
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


class CustomFormatter(logging.Formatter):
    """
    Custom formatter yang mendeteksi log dari middleware (API hits).
    - API hits: timestamp | level | message
    - Log lainnya: timestamp | level | name | filename:line | message
    """
    
    def __init__(self):
        super().__init__(datefmt=DATE_FORMAT)
    
    def format(self, record: logging.LogRecord) -> str:
        # Cek apakah message mengandung pattern API hit (Request/Response dengan request_id)
        msg = str(record.msg)
        is_api_log = msg.startswith("[") and ("] Request:" in msg or "] Response:" in msg or "] Error:" in msg)
        
        if is_api_log:
            # Format simple untuk API hits
            self._style._fmt = "%(asctime)s | %(levelname)-8s | %(message)s"
        else:
            # Format lengkap untuk log lainnya
            self._style._fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
        
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup logging configuration untuk FastAPI.
    Configure ROOT logger supaya semua module dapat handlers.
    """
    global _initialized
    
    if _initialized:
        return logging.getLogger("app")
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    formatter = CustomFormatter()
    
    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 2. File Handler - All logs (rotating by size)
    all_log_file = os.path.join(LOG_DIR, "app.log")
    file_handler = RotatingFileHandler(
        all_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 3. Error File Handler - Error logs only
    error_log_file = os.path.join(LOG_DIR, "error.log")
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # 4. Daily rotating log file
    daily_log_file = os.path.join(LOG_DIR, "daily.log")
    daily_handler = TimedRotatingFileHandler(
        daily_log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    daily_handler.setLevel(logging.INFO)
    daily_handler.setFormatter(formatter)
    daily_handler.suffix = "%Y-%m-%d"
    root_logger.addHandler(daily_handler)

    _initialized = True
    
    return logging.getLogger("app")


def get_logger(name: str = "app") -> logging.Logger:
    """Get logger instance by name."""
    return logging.getLogger(name)