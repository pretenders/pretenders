import base64
import json
import re
import traceback


from bottle import request, response, route, HTTPResponse
from bottle import delete, get, post
from bottle import run as run_bottle

from pretenders.base import SubClient

BOSS_URL = ''
REQUEST_ONLY_HEADERS = ['User-Agent', 'Connection', 'Host', 'Accept']
boss_client = None

def acceptable_response_header(header):
    "Use to filter which HTTP headers in the request should be removed"
    return not (header.startswith('X-Pretend-') or
                header in REQUEST_ONLY_HEADERS)


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
    return request.headers.get(header, default)


@route('/mock<url:path>', method='ANY')
def replay(url):
    """
    Replay a previously recorded preset, and save the request in history
    """
    relative_url = url
    if request.query_string:
        relative_url = "{0}?{1}".format(relative_url, request.query_string)
    body = {
        'body': base64.b64encode(request.body.read()).decode('ascii'),
        'headers': to_dict(request.headers),
        'method': request.method,
        'url': relative_url,
        'match': [relative_url, request.method],
    }
    body = json.dumps(body)
    boss_response = boss_client.http('POST', url="/mock", body=body)
    if boss_response.status == 200:
        content = boss_response.read().decode('ascii')
        preset = json.loads(content)
        for header, value in preset['headers'].items():
            response.set_header(header, value)
        response.status = preset['status']
        return preset['body']
    else:
        raise HTTPResponse(boss_response.read(),
                           status=boss_response.status)


def run(host='localhost', port=8000, boss_url=''):
    "Start the mock HTTP server"
    global BOSS_URL, boss_client
    BOSS_URL = boss_url
    boss_client = SubClient(boss_url, '')
    run_bottle(host=host, port=port, reloader=True)


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Start the server')
    parser.add_argument('-H', '--host', dest='host', default='localhost',
                help='host/IP to run the server on (default: localhost)')
    parser.add_argument('-p', '--port', dest='port', type=int, default=8001,
                help='port number to run the server on (default: 8001)')
    parser.add_argument('-b', '--boss', dest='boss_url',
                        default='localhost:8000',
                        help="url for accessing the Boss server.")
    args = parser.parse_args()
    pid = os.getpid()
    with open('pretender-http.pid', 'w') as f:
        f.write(str(pid))
    # bottle.debug(True)
    run(args.host, args.port, args.boss_url)
