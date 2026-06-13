import logging
from pathlib import Path
from dataclasses import asdict
from .config import LoggingConfig
from .formatters import ColoredFormatter, BaseFormatter, TelegramFormatter
from .telegram import TelegramHandler
from . import priority_info #ensures the monkey patch is setup

def _mask_token(token: str | None) -> str | None:
    if not token:
        return token

    # Telegram tokens are usually: <digits>:<secret>
    if ':' in token:
        prefix, secret = token.split(':', 1)

        if len(secret) <= 6:
            masked = '*' * len(secret)
        else:
            masked = f"{secret[:3]}***{secret[-3:]}"

        return f"{prefix}:{masked}"

    return "***MASKED***"

def get_logger(program_name: str, cfg: LoggingConfig) -> logging.Logger:
    """Initialise the logger for the application.

    ``cfg`` must be an instance of :class:`LoggingConfig`.
    """
    logger = logging.getLogger(program_name)
    logger.setLevel(logging.DEBUG if cfg.verbose else logging.INFO)

    # Console handler with optional colour output
    console_handler = logging.StreamHandler()
    try:
        console_handler.setFormatter(ColoredFormatter())
    except Exception:
        console_handler.setFormatter(BaseFormatter())
    logger.addHandler(console_handler)

    # File handler
    if cfg.log_file_path:
        log_path = Path(cfg.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(BaseFormatter())
        logger.addHandler(file_handler)
    else:
        logger.info("No log_file_path specified, disabling log to file.")

    # Telegram handler (plain formatting)
    if cfg.telegram_bot_token and cfg.level_chat_ids:
        telegram_handler = TelegramHandler(
            bot_token=cfg.telegram_bot_token,
            level_chat_ids=cfg.level_chat_ids,
        )
        telegram_handler.setLevel(logging.DEBUG)
        telegram_handler.setFormatter(TelegramFormatter())
        logger.addHandler(telegram_handler)
    else:
        logger.info("No telegram_bot_token or level_chat_ids specified, disabling log to Telegram.")

    logger.propagate = False

    debug_config = asdict(cfg)
    debug_config["telegram_bot_token"] = _mask_token(debug_config.get("telegram_bot_token"))
    logger.debug("tglogging configuration loaded: %s", debug_config)

    return logger
