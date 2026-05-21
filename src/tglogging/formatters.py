import logging
import datetime

class BaseFormatter(logging.Formatter):
    """Simple log record formatter used by file and telegram handlers."""

    def _format_message(self, record: logging.LogRecord) -> str:
        timestamp = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return f"[{record.name}][{record.levelname}] {timestamp} - {record.getMessage()}"

    def format(self, record: logging.LogRecord) -> str:
        return self._format_message(record)

class ColoredFormatter(BaseFormatter):
    COLORS = {
        'DEBUG': '\033[90m',        # Grey
        'INFO': '\033[94m',         # Blue
        'PRIORITY_INFO': '\033[94m',# Blue (same as INFO)
        'WARNING': '\033[93m',      # Yellow
        'ERROR': '\033[91m',        # Red
        'CRITICAL': '\033[41m',     # Red background
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        formatted = self._format_message(record)
        return f"{color}{formatted}{self.RESET}"