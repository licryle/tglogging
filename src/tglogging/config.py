from dataclasses import dataclass, field
from typing import Dict, List, Union

@dataclass(frozen=True)
class LoggingConfig:
    """Immutable holder for all configuration needed by tglogging.

    Validation is performed in ``__post_init__`` to ensure:
    * ``log_file_path`` is a non‑empty string.
    * ``telegram_bot_token`` may be ``None`` or a non‑empty string.
    * ``level_chat_ids`` is a mapping from ``int`` logging levels to
      ``list`` of chat‑id strings. Each chat‑id may be ``"<chat_id>"``
      or ``"<chat_id>:<thread_id>"`` / ``"<chat_id>_<thread_id>"``.
    """
    log_file_path: str = "./data/logs/yt2podcast.log"
    telegram_bot_token: Union[str, None] = None
    level_chat_ids: Dict[int, List[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.log_file_path, str) or not self.log_file_path:
            raise ValueError("log_file_path must be a non‑empty string")
        if self.telegram_bot_token is not None and (
            not isinstance(self.telegram_bot_token, str) or not self.telegram_bot_token
        ):
            raise ValueError("telegram_bot_token must be a non‑empty string or None")
        if not isinstance(self.level_chat_ids, dict):
            raise TypeError("level_chat_ids must be a dict mapping int levels to list of chat ids")
        for level, chats in self.level_chat_ids.items():
            if not isinstance(level, int):
                raise TypeError("level_chat_ids keys must be ints representing logging levels")
            if not isinstance(chats, (list, tuple)):
                raise TypeError("level_chat_ids values must be lists of chat id strings")
            for chat in chats:
                if not isinstance(chat, str) or not chat:
                    raise TypeError("each chat id must be a non‑empty string")
                if ':' in chat:
                    parts = chat.split(':')
                    if len(parts) != 2 or not parts[1].isdigit():
                        raise ValueError(f"Invalid thread suffix in chat id '{chat}'")
                elif '_' in chat:
                    parts = chat.split('_')
                    if len(parts) != 2 or not parts[1].isdigit():
                        raise ValueError(f"Invalid thread suffix in chat id '{chat}'")
