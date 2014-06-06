import logging
try:
    from logging.config import dictConfig
except ImportError:
    # Backwards compatible with py < 2.7
    from pretenders.common.compat.dictconfig import dictConfig

from pretenders.server import settings


def setup_logging():
    if not settings.LOGGING_STARTED:
        dictConfig(settings.LOGGING_CONFIG)
        settings.LOGGING_STARTED = True


def get_logger(name):
    setup_logging()
    return logging.getLogger(name)
