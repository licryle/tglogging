"""Example script demonstrating tglogging usage.

Run this file after installing the package (e.g., `pip install -e .`).
It configures a TGLoggingConfig, initialises logging, and emits a few log messages.
"""

import logging
from tglogging import configure_logger, LoggingConfig

# Replace the placeholders with your actual Telegram bot token and chat ID.
config = LoggingConfig(
    log_file_path="./log.txt",
    telegram_bot_token="YOUR_TELEGRAM_BOT_TOKEN",
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
logger = configure_logger('AppName', config, verbose=True)

logger.debug("This is a DEBUG message – will appear only if level is DEBUG.")
logger.info("Informational message sent to stdout and Telegram.")
logger.priority_info("Informational message you want to get attention from, even if not an error.")
logger.warning("Warning! Something might be amiss.")
logger.error("Error encountered – also forwarded to Telegram.")
logger.critical("Critical failure – immediate attention required!")
