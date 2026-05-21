import logging
import json
import urllib.request
import urllib.error
import html
from typing import Union, List, Dict

def _send_telegram_message(token: str, chat_id: str, message: str) -> None:
    """Helper to POST a message to Telegram Bot API.

    Supports optional thread ID for sending to a specific topic.
    Chat IDs can be provided as "<chat_id>", "<chat_id>:<thread_id>", or "<chat_id>_<thread_id>".
    """
    if not token or not chat_id:
        return
    # Determine separator (':' or '_' ) and split, stripping whitespace
    sep: Union[str, None] = None
    if ':' in chat_id:
        sep = ':'
    elif '_' in chat_id:
        sep = '_'
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
            response.read()
    except urllib.error.HTTPError as e:
        logging.getLogger(__name__).error(f"Telegram API HTTPError {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        logging.getLogger(__name__).error(f"Telegram API URLError: {e.reason}")
    except Exception as e:
        logging.getLogger(__name__).error(f"Unexpected error sending Telegram message: {e}")

class TelegramHandler(logging.Handler):
    """Handler that sends log records to Telegram.

    The handler expects a valid ``bot_token`` (or ``None`` to noop) and a
    ``level_chat_ids`` mapping that has already been validated by
    ``LoggingConfig``.
    """

    def __init__(self, bot_token: Union[str, None], level_chat_ids: Dict[int, List[str]]) -> None:
        super().__init__()
        self.level = logging.NOTSET
        self.bot_token = bot_token
        self.level_chat_ids = level_chat_ids
        # Validate level_chat_ids structure: keys must be int logging levels, values list of non-empty strings
        if not isinstance(self.level_chat_ids, dict):
            raise TypeError("level_chat_ids must be a dict mapping int levels to list of chat ids")
        for level, chats in self.level_chat_ids.items():
            if not isinstance(level, int):
                raise TypeError("level_chat_ids keys must be ints representing logging levels")
            if not isinstance(chats, (list, tuple)):
                raise TypeError("level_chat_ids values must be lists of chat id strings")
            for chat in chats:
                if not isinstance(chat, str) or not chat:
                    raise TypeError("each chat id must be a non-empty string")
                if ':' in chat:
                    parts = chat.split(':')
                    if len(parts) != 2 or not parts[1].isdigit():
                        raise ValueError(f"Invalid thread suffix in chat id '{chat}'")
                elif '_' in chat:
                    parts = chat.split('_')
                    if len(parts) != 2 or not parts[1].isdigit():
                        raise ValueError(f"Invalid thread suffix in chat id '{chat}'")

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