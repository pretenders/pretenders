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


class APIHelper(object):

    def __init__(self, connection, path):
        self.connection = connection
        self.path = path

    def http(self, method, *args, **kwargs):
        self.connection.request(method=method, *args, **kwargs)
        return self.connection.getresponse()

    def get(self, id):
        return self.http('GET', url='{0}/{1}'.format(self.path, id))

    def list(self, filters={}):
        query_string = ''
        if filters:
            query_string = '?{0}'.format(urllib.urlencode(filters))
        url = '{0}{1}'.format(self.path, query_string)
        return self.http('GET', url=url)

    def reset(self):
        return self.http('DELETE', url=self.path)
