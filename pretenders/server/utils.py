import bottle

from pretenders.server.log import get_logger
from pretenders.common.constants import REQUEST_ONLY_HEADERS

LOGGER = get_logger('pretenders.server.utils')


def acceptable_response_header(header):
    "Use to filter which HTTP headers in the request should be removed"
    return header not in REQUEST_ONLY_HEADERS


def get_header(header, default=None):
    return bottle.request.headers.get(header, default)
