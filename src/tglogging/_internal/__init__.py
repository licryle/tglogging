"""Internal subpackage for tglogging.

This package contains the implementation modules that are not part of the public API.
Modules:
- tglogging: configure_logger and LoggingConfig implementation
- telegram: TelegramHandler and _send_telegram_message
- config: LoggingConfig dataclass (re-exported for convenience)
- formatters: BaseFormatter, ColoredFormatter
- priority_info: PRIORITY_INFO constant and related utilities

Only the symbols listed in __all__ are intended for internal use.
"""

# Re-export core implementations for internal use
from ..tglogging import configure_logger, LoggingConfig
from ..telegram import TelegramHandler, _send_telegram_message
from ..config import LoggingConfig as ConfigClass
from ..formatters import BaseFormatter, ColoredFormatter
from ..priority_info import PRIORITY_INFO

__all__ = [
    "configure_logger",
    "LoggingConfig",
    "ConfigClass",
    "TelegramHandler",
    "_send_telegram_message",
    "BaseFormatter",
    "ColoredFormatter",
    "PRIORITY_INFO",
]
