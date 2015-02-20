import logging
try:
    from logging.config import dictConfig
except ImportError:
    # Backwards compatible with py < 2.7
    from pretend_extended.common.compat.dictconfig import dictConfig

from pretend_extended.server import settings


def setup_logging():
    if not settings.LOGGING_STARTED:
        dictConfig(settings.LOGGING_CONFIG)
        settings.LOGGING_STARTED = True


def get_logger(name):
    setup_logging()
    logging.getLogger(name).setLevel(logging.CRITICAL)
    return logging.getLogger(name)
