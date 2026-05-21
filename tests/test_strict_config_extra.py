import logging
import pytest
from tglogging import LoggingConfig
from tglogging.tglogging import TelegramHandler, _send_telegram_message

class DummySender:
    def __init__(self):
        self.calls = []
    def __call__(self, token, chat_id, message):
        self.calls.append((token, chat_id, message))

# Configuration validation tests

def test_invalid_level_key_type():
    """Level keys must be ints; using a string should raise TypeError."""
    with pytest.raises(TypeError):
        LoggingConfig(level_chat_ids={"ERROR": ["123"]})

def test_invalid_chat_ids_type():
    """Level values must be list/tuple; using a string should raise TypeError."""
    with pytest.raises(TypeError):
        LoggingConfig(level_chat_ids={logging.ERROR: "not-a-list"})

def test_invalid_chat_id_empty_string():
    """Chat IDs cannot be empty strings; should raise TypeError."""
    with pytest.raises(TypeError):
        LoggingConfig(level_chat_ids={logging.ERROR: [""]})

def test_invalid_thread_suffix_non_digit():
    """Thread suffix must be numeric; non‑digit should raise ValueError."""
    with pytest.raises(ValueError):
        LoggingConfig(level_chat_ids={logging.ERROR: ["123:abc"]})
    with pytest.raises(ValueError):
        LoggingConfig(level_chat_ids={logging.ERROR: ["123_abc"]})

# TelegramHandler behavior tests

def test_telegram_handler_no_token(monkeypatch):
    dummy = DummySender()
    monkeypatch.setattr('tglogging.tglogging._send_telegram_message', dummy)
    handler = TelegramHandler(bot_token=None, level_chat_ids={logging.ERROR: ["123"]})
    logger = logging.getLogger("tglogging.test_no_token")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.error("ignored message")
    assert dummy.calls == []

def test_telegram_handler_sends_message(monkeypatch):
    dummy = DummySender()
    monkeypatch.setattr('tglogging.tglogging._send_telegram_message', dummy)
    token = "dummy-token"
    chat_id = "321"
    handler = TelegramHandler(bot_token=token, level_chat_ids={logging.ERROR: [chat_id]})
    logger = logging.getLogger("tglogging.test_send")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.error("test msg")
    assert len(dummy.calls) == 1
    sent_token, sent_chat, sent_msg = dummy.calls[0]
    assert sent_token == token
    assert sent_chat == chat_id
    assert "test msg" in sent_msg

def test_telegram_handler_respects_level(monkeypatch):
    dummy = DummySender()
    monkeypatch.setattr('tglogging.tglogging._send_telegram_message', dummy)
    handler = TelegramHandler(bot_token="tok", level_chat_ids={logging.ERROR: ["123"]})
    logger = logging.getLogger("tglogging.level_test")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    # INFO should not trigger send
    logger.info("info should not send")
    # ERROR should trigger send
    logger.error("error should send")
    assert len(dummy.calls) == 1
    _, chat, msg = dummy.calls[0]
    assert chat == "123"
    assert "error should send" in msg
