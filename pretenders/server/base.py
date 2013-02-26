import logging
try:
    from logging.config import dictConfig
except ImportError:
    # Backwards compatible with py < 2.7
    from pretenders.compat.dictconfig import dictConfig
import os
import urllib

from pretenders import settings


def in_parent_process():
    return os.environ.get('BOTTLE_CHILD', 'false') != 'true'


def save_pid_file(filename):
    # Save PID to disk
    pid = os.getpid()
    with open(filename, 'w') as f:
        f.write(str(pid))


def setup_logging():
    if not settings.LOGGING_STARTED:
        dictConfig(settings.LOGGING_CONFIG)
        settings.LOGGING_STARTED = True


def get_logger(name):
    setup_logging()
    return logging.getLogger(name)


class ResourceNotFound(Exception):
    pass


class UnexpectedResponseStatus(Exception):
    pass
