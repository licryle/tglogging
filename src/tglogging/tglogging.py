import logging
import urllib.request
import urllib.error
import json
import html
from pathlib import Path
import datetime
from typing import Dict, List, Union
from dataclasses import dataclass, field
from .config import LoggingConfig
from .formatters import ColoredFormatter, BaseFormatter
from .telegram import TelegramHandler
from . import priority_info #ensures the monkey patch is setup

def configure_logger(program_name: str, cfg: LoggingConfig, verbose: bool = False) -> logging.Logger:
    """Initialise the logger for the application.

    ``cfg`` must be an instance of :class:`LoggingConfig`.
    ``verbose`` forces the logger to ``DEBUG`` level.
    """
    logger = logging.getLogger(program_name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # File handler
    log_path = Path(cfg.log_file_path)
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(BaseFormatter())
        logger.addHandler(file_handler)

    # Console handler with optional colour output
    console_handler = logging.StreamHandler()
    try:
        console_handler.setFormatter(ColoredFormatter())
    except Exception:
        console_handler.setFormatter(BaseFormatter())
    logger.addHandler(console_handler)

    # Telegram handler (plain formatting)
    telegram_handler = TelegramHandler(
        bot_token=cfg.telegram_bot_token,
        level_chat_ids=cfg.level_chat_ids,
    )
    telegram_handler.setLevel(logging.DEBUG)
    telegram_handler.setFormatter(BaseFormatter())
    logger.addHandler(telegram_handler)

    return logger
