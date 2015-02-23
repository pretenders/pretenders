import bottle

from pretend_extended.server.log import get_logger
from pretend_extended.common.constants import REQUEST_ONLY_HEADERS

LOGGER = get_logger('pretend_extended.server.utils')


def acceptable_response_header(header):
    "Use to filter which HTTP headers in the request should be removed"
    return header not in REQUEST_ONLY_HEADERS


def get_header(header, default=None):
    return bottle.request.headers.get(header, default)
