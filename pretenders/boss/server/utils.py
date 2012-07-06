import logging
import os
import signal
import subprocess
import sys

import bottle

try:
    from collections import OrderedDict
except ImportError:
    #2.6 compatibility
    from pretenders.compat.ordered_dict import OrderedDict

from pretenders.boss.server import data

LOGGER = logging.getLogger('pretenders.boss.server.utils')


def acceptable_response_header(header):
    "Use to filter which HTTP headers in the request should be removed"
    return header not in data.REQUEST_ONLY_HEADERS


def to_dict(wsgi_headers, include=lambda _: True):
    """
    Convert WSGIHeaders to a dict so that it can be JSON-encoded
    """
    ret = {}
    for k, v in wsgi_headers.items():
        if include(k):
            ret[k] = v
    return ret


def get_header(header, default=None):
    return bottle.request.headers.get(header, default)


def delete_mock_server(uid):
    "Delete a mock server by ``uid``"
    LOGGER.info("Performing delete on {0}".format(uid))
    pid = data.HTTP_MOCK_SERVERS[uid].pid
    LOGGER.info("attempting to kill pid {0}".format(pid))
    os.kill(pid, signal.SIGINT)
    del data.HTTP_MOCK_SERVERS[uid]


def run_maintainer():
    """
    Run the maintainer - pruning the number of mock servers running.

    :returns:
        The pid of the maintainer process.
    """
    process = subprocess.Popen([
            sys.executable,
            "-m",
            "pretenders.boss.maintain",
            "-H", "localhost",
            "-p", str(data.BOSS_PORT),
            ],
    )
    return process.pid
