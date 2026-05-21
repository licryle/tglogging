import logging
import os
import urllib.request
import json
from pathlib import Path
import datetime

# Helper to build a consistent log line (used by both console and Telegram)
def _format_message(record: logging.LogRecord, program_name: str) -> str:
    timestamp = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
    return f"[{program_name}][{record.levelname}] {timestamp} - {record.name} - {record.getMessage()}"


# Define custom log level for special priority information
PRIORITY_INFO = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(PRIORITY_INFO, "PRIORITY_INFO")

# Monkey-patch Logger to add a convenience method
def _priority_info(self, message, *args, **kwargs):
    if self.isEnabledFor(PRIORITY_INFO):
        self._log(PRIORITY_INFO, message, args, **kwargs)

logging.Logger.priority_info = _priority_info

# Default configuration values; can be overridden by environment variables
LOG_FILE_PATH = os.getenv('YT2PODCAST_LOG_FILE', './data/logs/yt2podcast.log')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Environment variables for per-level Telegram chat IDs (comma-separated lists)
def _parse_chat_ids(env_name: str) -> list[str]:
    ids = os.getenv(env_name)
    if not ids:
        return []
    return [cid.strip() for cid in ids.split(',') if cid.strip()]

# Mapping from logging level to its corresponding environment variable name
_LEVEL_CHAT_ENV = {
    logging.DEBUG: 'TELEGRAM_CHAT_IDS_DEBUG',
    logging.INFO: 'TELEGRAM_CHAT_IDS_INFO',
    PRIORITY_INFO: 'TELEGRAM_CHAT_IDS_PRIORITY_INFO',
    logging.WARNING: 'TELEGRAM_CHAT_IDS_WARNING',
    logging.ERROR: 'TELEGRAM_CHAT_IDS_ERROR',
    logging.CRITICAL: 'TELEGRAM_CHAT_IDS_CRITICAL',
}

# Pre-compute chat ID lists for each level
_LEVEL_CHAT_IDS = {level: _parse_chat_ids(env) for level, env in _LEVEL_CHAT_ENV.items()}

class TelegramHandler(logging.Handler):
    """Custom logging handler that sends log records to Telegram.
    It sends all records to the default chat, but records with level >= WARNING
    are also sent to the alert chat if configured.
    """
    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            # Send to main chat
            if TELEGRAM_BOT_TOKEN:
                # Determine target chat IDs based on log level
                chat_ids = _LEVEL_CHAT_IDS.get(record.levelno, [])
                for chat_id in chat_ids:
                    if chat_id:
                        _send_telegram_message(TELEGRAM_BOT_TOKEN, chat_id, msg)
        except Exception:
            self.handleError(record)

def _send_telegram_message(token: str, chat_id: str, message: str) -> None:
    """Helper to POST a message to Telegram Bot API.
    Supports optional thread ID for sending to a specific topic.
    Chat IDs can be provided as "<chat_id>", "<chat_id>:<thread_id>", or "<chat_id>_<thread_id>".
    """
    if not token or not chat_id:
        return
    # Determine separator (':' or '_' ) and split, stripping whitespace
    if ':' in chat_id:
        sep = ':'
    elif '_' in chat_id:
        sep = '_'
    else:
        sep = None
    if sep:
        parts = [p.strip() for p in chat_id.split(sep)]
        real_chat_id = parts[0]
        thread_id = int(parts[1]) if len(parts) > 1 and parts[1] else None
    else:
        real_chat_id = chat_id.strip()
        thread_id = None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": real_chat_id,
        "text": message,
        "parse_mode": "HTML",
    }
    if thread_id is not None:
        payload["message_thread_id"] = thread_id
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10):
        pass

def init_logging(program_name: str, verbose: bool = False) -> logging.Logger:
    """Initialise the root logger for a given program.
    Returns the configured logger instance.
    """
    logger = logging.getLogger(program_name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    # Ensure log directory exists
    log_path = Path(LOG_FILE_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # File handler with simple formatter
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_formatter = logging.Formatter(f'[{program_name}][%(levelname)s] %(asctime)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    # Console handler with optional color output
    console_handler = logging.StreamHandler()
    try:
        from colorama import init as colorama_init, Fore, Style
        colorama_init()
        class ColoredFormatter(logging.Formatter):
            COLORS = {
                'DEBUG': Fore.LIGHTBLACK_EX,
                'INFO': Fore.LIGHTBLUE_EX,
                'PRIORITY_INFO': Fore.MAGENTA,
                'WARNING': Fore.YELLOW,
                'ERROR': Fore.LIGHTRED_EX,
                'CRITICAL': Fore.RED + Style.BRIGHT,
            }
            RESET = Style.RESET_ALL
            def format(self, record: logging.LogRecord) -> str:
                color = self.COLORS.get(record.levelname, self.RESET)
                formatted = _format_message(record, program_name)
                return f"{color}{formatted}{self.RESET}"
        console_handler.setFormatter(ColoredFormatter())
    except Exception:
        console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.addHandler(console_handler)
    # Telegram handler for alerts and routing
    telegram_handler = TelegramHandler()
    telegram_handler.setLevel(logging.DEBUG)
    # Formatter for Telegram (plain, no colors) matching console layout
    class TelegramFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            return _format_message(record, program_name)
    telegram_handler.setFormatter(TelegramFormatter())
    logger.addHandler(telegram_handler)
    return logger
