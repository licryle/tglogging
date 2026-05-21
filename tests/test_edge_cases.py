import logging
import os
import pathlib
import pytest
from tglogging import LoggingConfig, configure_logger
from tglogging.tglogging import TelegramHandler

def test_invalid_log_file_path(tmp_path):
    # Provide a path to a directory without write permission (simulate by using a file path that is a directory)
    invalid_path = tmp_path / "nonexistent_dir" / "log.log"
    cfg = LoggingConfig(log_file_path=str(invalid_path), telegram_bot_token=None, level_chat_ids={})
    logger = configure_logger("testapp", cfg)
    assert isinstance(logger, logging.Logger)
    # Ensure the file was created
    assert pathlib.Path(cfg.log_file_path).exists()

def test_telegram_handler_missing_token_but_chat_ids():
    # Token is None but level_chat_ids is non‑empty; handler should silently ignore sending
    handler = TelegramHandler(bot_token=None, level_chat_ids={logging.ERROR: ["12345"]})
    logger = logging.getLogger("tglogging.edge")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    # No exception should be raised when logging an error
    logger.error("test message with no token")
    assert True

def test_invalid_level_chat_ids_type():
    # level_chat_ids keys must be ints; passing a str should raise TypeError when handler accesses it
    with pytest.raises(TypeError):
        TelegramHandler(bot_token="dummy", level_chat_ids={"ERROR": ["123"]})
