import base64
import json
import re
import socket
import traceback

from bottle import request, response, route, HTTPResponse
from bottle import run as run_bottle

from pretenders.boss.client import BossClient
from pretenders.http import Preset, RequestInfo
from pretenders.constants import RETURN_CODE_PORT_IN_USE

BOSS_PORT = ''
REQUEST_ONLY_HEADERS = ['User-Agent', 'Connection', 'Host', 'Accept']
boss_api_handler = None


def get_header(header, default=None):
    return request.headers.get(header, default)


@route('/mock/<uid:int>/<url:path>', method='ANY')
def replay(uid, url):
    """
    Replay a previously recorded preset, and save the request in history
    """
    f = open('/tmp/replay', 'a')
    f.write('replay in http.server called on {0}/{1}\n'.format(uid, url))

    request_info = RequestInfo(url, request)
    body = request_info.serialize()
    boss_url = "/mock/{0}".format(uid)
    f.write('forwarding to boss at {0} (port {1})\n'.format(boss_url, BOSS_PORT))

    boss_response = boss_api_handler.http(
        'POST',
        url=boss_url,
        body=body
    )
    f.write("boss replied with a {0}\n".format(boss_response.status))
    f.close()
    if boss_response.status == 200:
        preset = Preset(boss_response.read())
        return preset.as_http_response(response)
    else:
        raise HTTPResponse(boss_response.read(),
                           status=boss_response.status)


def run(host='localhost', port=8000, boss_port=''):
    "Start the mock HTTP server"
    global BOSS_PORT, boss_api_handler
    BOSS_PORT = boss_port
    boss_api_handler = BossClient(host, boss_port).boss_access
    run_bottle(host=host, port=port, reloader=True)


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Start the server')
    parser.add_argument('-H', '--host', dest='host', default='localhost',
                help='host/IP to run the server on (default: localhost)')
    parser.add_argument('-p', '--port', dest='port', type=int, default=8001,
                help='port number to run the server on (default: 8001)')
    parser.add_argument('-b', '--boss', dest='boss_port',
                        default='8000',
                        help="port for accessing the Boss server.")
    args = parser.parse_args()
    pid = os.getpid()
    with open('pretender-http.pid', 'w') as f:
        f.write(str(pid))
    # bottle.debug(True)

    try:
        run(args.host, args.port, args.boss_port)
    except socket.error:
        print("QUITING")
        import sys
        sys.exit(RETURN_CODE_PORT_IN_USE)
