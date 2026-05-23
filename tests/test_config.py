import logging
import pytest
import pathlib

from tglogging import LoggingConfig, configure_logger


def test_valid_config():
    cfg = LoggingConfig(
        log_file_path="log.txt",
        telegram_bot_token="token",
        level_chat_ids={logging.ERROR: ["123", "456:789"]},
    )
    assert cfg.level_chat_ids[logging.ERROR] == ["123", "456:789"]

def test_priority_info():
    cfg = LoggingConfig(
        log_file_path="log.txt",
        telegram_bot_token="token",
        level_chat_ids={logging.ERROR: ["123", "456:789"]},
    )
    logger = configure_logger("testapp", cfg)
    logger.priority_info("Hello")
    assert True

def test_invalid_log_file_path():
    with pytest.raises(ValueError):
        LoggingConfig(log_file_path="")


def test_invalid_token():
    with pytest.raises(ValueError):
        LoggingConfig(telegram_bot_token="")


def test_invalid_level_chat_ids_key_type():
    with pytest.raises(TypeError):
        LoggingConfig(level_chat_ids={"ERROR": ["123"]})


def test_invalid_level_chat_ids_value_type():
    with pytest.raises(TypeError):
        LoggingConfig(level_chat_ids={logging.ERROR: "not a list"})


def test_invalid_chat_id_type():
    with pytest.raises(TypeError):
        LoggingConfig(level_chat_ids={logging.ERROR: [123]})


def test_invalid_thread_suffix():
    with pytest.raises(ValueError):
        LoggingConfig(level_chat_ids={logging.ERROR: ["123:abc"]})

def test_invalid_log_file_path(tmp_path):
    # Provide a path to a directory without write permission (simulate by using a file path that is a directory)
    invalid_path = tmp_path / "nonexistent_dir" / "log.log"
    cfg = LoggingConfig(log_file_path=str(invalid_path), telegram_bot_token=None, level_chat_ids={})
    logger = configure_logger("testapp", cfg)
    assert isinstance(logger, logging.Logger)
    # Ensure the file was created
    assert pathlib.Path(cfg.log_file_path).exists()

def test_none_config(tmp_path):
    """Test logger configuration when both telegram_bot_token and log_file_path are None.
    The logger should be created with only the console handler and no file or telegram handlers.
    """
    cfg = LoggingConfig(
        log_file_path=None,
        telegram_bot_token=None,
        level_chat_ids={},
    )
    logger = configure_logger("noneapp", cfg)
    assert isinstance(logger, logging.Logger)
    # Expect only the console handler (StreamHandler) to be attached
    # The console handler is added first in configure_logger
    assert len(logger.handlers) == 1
    console_handler = logger.handlers[0]
    assert isinstance(console_handler, logging.StreamHandler)
    # Logging a message should not raise
    logger.info("test message")
