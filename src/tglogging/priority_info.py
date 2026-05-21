import logging

# Define custom log level for special priority information
PRIORITY_INFO = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(PRIORITY_INFO, "PRIORITY_INFO")

# Monkey-patch Logger to add a convenience method
def _priority_info(self, message, *args, **kwargs):
    if self.isEnabledFor(PRIORITY_INFO):
        self._log(PRIORITY_INFO, message, args, **kwargs)

logging.Logger.priority_info = _priority_info