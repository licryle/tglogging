import logging

import urllib.request
import json
import html
from pathlib import Path
import datetime

from typing import Dict, List

from dataclasses import dataclass, field


# Define custom log level for special priority information
PRIORITY_INFO = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(PRIORITY_INFO, "PRIORITY_INFO")

# Monkey-patch Logger to add a convenience method
def _priority_info(self, message, *args, **kwargs):
    if self.isEnabledFor(PRIORITY_INFO):
        self._log(PRIORITY_INFO, message, args, **kwargs)

logging.Logger.priority_info = _priority_info

# ------------------------------------------------------------
# Config container – independent of the logger implementation
# ------------------------------------------------------------

@dataclass(frozen=True)
class TGLoggingConfig:
    """Immutable holder for all configuration needed by tg_logging.
    The application creates this object at start‑up and passes it to
    ``init_logging``.  If ``None`` is given, ``init_logging`` falls back
    to reading the traditional environment variables (backwards
    compatibility).
    """
    log_file_path: str = "./data/logs/yt2podcast.log"
    telegram_bot_token: str | None = None
    # Mapping ``logging level -> list of chat IDs`` (strings).  The IDs may
    # contain an optional thread suffix ("<chat_id>:<thread_id>" or
    # "<chat_id>_<thread_id>") which ``_send_telegram_message`` will
    # interpret.
    level_chat_ids: Dict[int, List[str]] = field(default_factory=dict)

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
        "text": html.escape(message),
        "parse_mode": "HTML",
    }
    if thread_id is not None:
        payload["message_thread_id"] = thread_id
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            # Consume response to ensure request completes
            response.read()
    except urllib.error.HTTPError as e:
        logging.getLogger(__name__).error(f"Telegram API HTTPError {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        logging.getLogger(__name__).error(f"Telegram API URLError: {e.reason}")
    except Exception as e:
        logging.getLogger(__name__).error(f"Unexpected error sending Telegram message: {e}")

class TelegramHandler(logging.Handler):
    """Handler that sends log records to Telegram.
    ``bot_token`` and ``level_chat_ids`` are supplied by the caller – the
    module stays independent from any global ``os.getenv`` calls.
    """

    def __init__(self, bot_token: str | None, level_chat_ids: Dict[int, List[str]]) -> None:
        super().__init__()
        self.bot_token = bot_token
        self.level_chat_ids = level_chat_ids

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            if not self.bot_token:
                return
            chat_ids = self.level_chat_ids.get(record.levelno, [])
            for chat_id in chat_ids:
                if chat_id:
                    _send_telegram_message(self.bot_token, chat_id, msg)
        except Exception:
            self.handleError(record)

class Formatter(logging.Formatter):
    def __init__(self, program_name: str):
        super().__init__()
        self.program_name = program_name

    def _format_message(self, record: logging.LogRecord) -> str:
        timestamp = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return f"[{self.program_name}][{record.levelname}] {timestamp} - {record.name} - {record.getMessage()}"

    def format(self, record: logging.LogRecord) -> str:
        return self._format_message(record)

class ColoredFormatter(Formatter):
    COLORS = {
        'DEBUG': '\033[90m',    # Grey
        'INFO': '\033[94m',     # Blue
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[41m', # Red background
    }
    RESET = '\033[0m'
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        formatted = self._format_message(record)
        return f"{color}{formatted}{self.RESET}"

def init_logging(program_name: str, cfg: TGLoggingConfig, verbose: bool = False) -> logging.Logger:
    """Initialise the logger for the application."""

    logger = logging.getLogger(program_name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # File handler
    log_path = Path(cfg.log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_formatter = logging.Formatter(
        f'[{program_name}][%(levelname)s] %(asctime)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler with optional colour output
    console_handler = logging.StreamHandler()
    try:
        console_handler.setFormatter(ColoredFormatter(program_name))
    except Exception:
        console_handler.setFormatter(Formatter(program_name))
    logger.addHandler(console_handler)

    # Telegram handler (plain formatting)
    telegram_handler = TelegramHandler(
        bot_token=cfg.telegram_bot_token,
        level_chat_ids=cfg.level_chat_ids,
    )
    telegram_handler.setLevel(logging.DEBUG)
    telegram_handler.setFormatter(Formatter(program_name))
    logger.addHandler(telegram_handler)

    return logger
