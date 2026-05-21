import logging
import pytest

from tglogging import LoggingConfig


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


def test_valid_config():
    cfg = LoggingConfig(
        log_file_path="log.txt",
        telegram_bot_token="token",
        level_chat_ids={logging.ERROR: ["123", "456:789"]},
    )
    assert cfg.level_chat_ids[logging.ERROR] == ["123", "456:789"]
