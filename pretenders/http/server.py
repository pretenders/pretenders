import socket

import bottle
from bottle import route, HTTPResponse

from pretenders.base import get_logger, in_parent_process, save_pid_file
from pretenders.boss.client import BossClient
from pretenders.constants import RETURN_CODE_PORT_IN_USE
from pretenders.http import Preset, RequestSerialiser

LOGGER = get_logger('pretenders.http.server')
BOSS_PORT = ''
boss_api_handler = None
UID = None


def get_header(header, default=None):
    return bottle.request.headers.get(header, default)


@route('<url:path>', method='ANY')
def replay(url):
    """
    Replay a previously recorded preset, and save the request in history
    """
    request_info = RequestSerialiser(url, bottle.request)
    body = request_info.serialize()
    LOGGER.info("Replaying URL for request: \n{0}".format(body))
    boss_response = boss_api_handler.http(
                        'POST',
                        url="/replay/{0}".format(UID),
                        body=body)
    if boss_response.status == 200:
        preset = Preset(boss_response.read())
        return preset.as_http_response(bottle.response)
    else:
        LOGGER.error("Cannot find matching request\n{0}".format(body))
        raise HTTPResponse(boss_response.read(),
                           status=boss_response.status)


def run(uid, host='localhost', port=8000, boss_port=''):
    "Start the mock HTTP server"
    global BOSS_PORT, boss_api_handler, UID
    BOSS_PORT = boss_port
    UID = uid
    boss_api_handler = BossClient(host, boss_port).boss_access
    if in_parent_process():
        save_pid_file('pretenders-mock-{0}.pid'.format(uid))
    bottle.run(host=host, port=port, reloader=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Start the server')
    parser.add_argument('-H', '--host', dest='host', default='localhost',
                help='host/IP to run the server on (default: localhost)')
    parser.add_argument('-p', '--port', dest='port', type=int, default=8001,
                help='port number to run the server on (default: 8001)')
    parser.add_argument('-b', '--boss', dest='boss_port', default='8000',
                help="port for accessing the Boss server.")
    parser.add_argument('-d', '--debug', dest="debug", default=False,
                action="store_true",
                help='start a build right after creation')
    parser.add_argument('-i', '--uid', dest='uid')
    args = parser.parse_args()
    bottle.debug(args.debug)

    try:
        run(args.uid, args.host, args.port, args.boss_port)
    except socket.error:
        LOGGER.info("QUITTING")
        import sys
        sys.exit(RETURN_CODE_PORT_IN_USE)
