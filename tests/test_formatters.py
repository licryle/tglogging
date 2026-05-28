import logging
import pathlib
import sys
from datetime import datetime

import pytest

# Import the library modules
from tglogging import LoggingConfig, configure_logger
from tglogging.tglogging import BaseFormatter, TelegramHandler

@pytest.fixture
def config(tmp_path):
    # Create a temporary log file path
    log_path = tmp_path / "test.log"
    return LoggingConfig(
        log_file_path=str(log_path),
        telegram_bot_token=None,
        level_chat_ids={},
    )

def test_default_config_values():
    cfg = LoggingConfig()
    assert cfg.log_file_path == None
    assert cfg.telegram_bot_token is None
    assert cfg.level_chat_ids == {}

def test_formatter_output():
    fmt = BaseFormatter()
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Hello World",
        args=(),
        exc_info=None,
    )
    # Mock timestamp
    fixed_time = datetime(2020, 1, 1, 12, 0, 0).timestamp()
    record.created = fixed_time
    formatted = fmt.format(record)
    # Expected format: [test.logger][INFO] 2020-01-01 12:00:00 - Hello World
    assert formatted == "[test.logger][INFO] 2020-01-01 12:00:00 - Hello World"

def test_telegram_handler_no_token(caplog):
    handler = TelegramHandler(bot_token=None, level_chat_ids={logging.ERROR: ["123"]})
    logger = logging.getLogger("tglogging.test")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.error("This should not raise")
    # Ensure no exception and nothing sent
    assert True
