import bottle

try:
    from collections import OrderedDict
except ImportError:
    #2.6 compatibility
    from pretenders.compat.ordered_dict import OrderedDict

from pretenders.log import get_logger
from pretenders.constants import REQUEST_ONLY_HEADERS

LOGGER = get_logger('pretenders.server.utils')


def acceptable_response_header(header):
    "Use to filter which HTTP headers in the request should be removed"
    return header not in REQUEST_ONLY_HEADERS


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
