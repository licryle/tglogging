# 📚 tglogging

## Overview
`tglogging` is a tiny logging utility that aligns logs, standard output, and Telegram notifications. It provides a simple API to configure logging handlers that can forward log messages to Telegram, making it easy to monitor long‑running scripts and services.

---

## 🛠️ Nix Development Environment
The repository ships a **Flake** that defines a development shell with all required dependencies.

```sh
# Clone the repository (if you haven't yet)
git clone https://github.com/yourusername/tglogging.git
cd tglogging

# Enter the Nix development shell (requires Nix with flakes enabled)
direnv alow # first time only
```

The `devShell` includes:
- Python 3.11
- `setuptools` & `wheel`
- `pytest` for running tests
- `pygments` (used by the library for coloured output)

You can also inspect the flake definition in `flake.nix`.

---

## 🚀 Usage
```python
import logging
from tglogging import get_logger, LoggingConfig

# Replace the placeholders with your actual Telegram bot token and chat ID.
config = LoggingConfig(
    log_file_path="./log.txt",
    telegram_bot_token="YOUR_TELEGRAM_BOT_TOKEN",
    verbose=True,
    level_chat_ids= {
        logging.DEBUG:          ['00:0'],         # Debug
        logging.INFO:           ['00:0'],         # Info
        logging.PRIORITY_INFO:  ['00:0','11'],    # Priority Info > 2 channels for example
        logging.WARNING:        ['00:0'],         # Warning
        logging.ERROR:          ['00:0','11'],    # Error
        logging.CRITICAL:       ['00:0','11'],    # Critical
    }
)

# Initialise the logging system with the TGLoggingConfig.
logger = get_logger('AppName', config)

logger.debug("This is a DEBUG message – will appear only if level is DEBUG.")
logger.info("Informational message sent to stdout and Telegram.")
logger.priority_info("Informational message you want to get attention from, even if not an error.")
logger.warning("Warning! Something might be amiss.")
logger.error("Error encountered – also forwarded to Telegram.")
logger.critical("Critical failure – immediate attention required!")
```

> **Note:** `get_logger` sets `logger.propagate = False` to prevent log records from bubbling up to ancestor loggers, avoiding duplicate output. You can reactivate on the returned object from `get_logger`.

The library ships a `TelegramHandler` that forwards log records to the Telegram Bot API. See the `src/tglogging/telegram.py` module for details.

---

## 📦 Build & Install
The project uses a standard `pyproject.toml`/`setuptools` setup.

```sh
# Build the wheel
python -m build

# Install locally (editable mode during development)
pip install -e .
```

---

## ✅ Testing
Run the test suite with pytest (the `devShell` already provides it):

```sh
pytest
```

All tests are located under the `tests/` directory.

---

## 📁 Project Layout
```
.
├── README.md            # <-- You are reading it!
├── flake.nix            # Nix flake defining the dev environment
├── pyproject.toml       # Build metadata
├── src/                # Library source code
│   └── tglogging/      # Python package
├── tests/               # Test suite
└── sample/              # Example scripts (e.g., `example.py`)
```

---

## 👋 Contributing
Feel free to open issues or submit pull requests. Make sure new code follows the existing style and includes tests.

---

## 📜 License
This project is licensed under the MIT License. See the `LICENSE` file for details.
