import json
import re
import traceback
try:
    from collections import OrderedDict
except ImportError:
    #2.6 compatibility
    from pretenders.compat.ordered_dict import OrderedDict

from bottle import request, response, route, HTTPResponse
from bottle import delete, get, post
from bottle import run as run_bottle


REQUEST_ONLY_HEADERS = ['User-Agent', 'Connection', 'Host', 'Accept']

presets = OrderedDict()
history = []


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


def pop_preset(preset_list, key):
    del preset_list[0]
    if not preset_list:
        del presets[key]


def select_preset(values):
    """Select a preset to respond with.

    Look through the presets for a match. If one is found pop off a preset
    response and return it.

    ``values`` is a tuple of values to match against the regexes stored in
    presets. They are assumed to be in the same sequence as those of the
    regexes.

    Return 404 if no preset found that matches.
    """
    url_match = False
    for key, preset_list in presets.items():
        preset = preset_list[0]
        preset_matches = True
        for rule, value in zip(preset["rules"], values):
            if not re.match(rule, value):
                preset_matches = False
                break

        if preset_matches:
            pop_preset(preset_list, key)
            return preset

    raise HTTPResponse(b"No matching preset response", status=404)


@post('/mock')
def replay():
    """
    Replay a previously recorded preset, and save the request in history
    """
    print(presets)
    if not len(presets):
        raise HTTPResponse(b"No preset response", status=404)
    mock_request = json.loads(request.body.read().decode('ascii'))
    history.append(mock_request)

    preset = select_preset(mock_request['match'])
    response.content_type = 'application/json'
    return json.dumps(preset)


@post('/preset')
def add_preset():
    """
    Save the incoming request body as a preset response
    """
    preset_body = request.body.read().decode('ascii')
    new_preset = json.loads(preset_body)
    rule = tuple(new_preset['rules'])
    if rule not in presets:
        presets[rule] = []

    url_presets = presets[rule]
    url_presets.append(new_preset)


@delete('/preset')
def clear_presets():
    """
    Delete all recorded presets
    """
    presets.clear()


@get('/history/<ordinal:int>')
def get_history(ordinal):
    """
    Access requests issued to the mock server
    """
    try:
        saved = history[ordinal]
        for header, value in saved['headers'].items():
            if acceptable_response_header(header):
                response.set_header(header, value)
        response.set_header('X-Pretend-Request-Method', saved['method'])
        response.set_header('X-Pretend-Request-Url', saved['url'])
        return saved['body']
    except IndexError:
        raise HTTPResponse(b"No recorded request", status=404)
    except Exception:
        traceback.print_exc()


@delete('/history')
def clear_history():
    """
    Delete all recorded requests
    """
    del history[:]


@get('/http_mock')
def http_mock():
    """
    Client is requesting an http mock instance.

    Launch an http mock instance on a random unused port.
    Keep track of the pid of the mock instance
    Kill the mock instance after timeout expired.
    Return the location of the mock instance.
    """
    pass


def run(host='localhost', port=8000):
    "Start the mock HTTP server"
    run_bottle(host=host, port=port, reloader=True)


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Start the server')
    parser.add_argument('-H', '--host', dest='host', default='localhost',
                help='host/IP to run the server on (default: localhost)')
    parser.add_argument('-p', '--port', dest='port', type=int, default=8000,
                help='port number to run the server on (default: 8000)')

    args = parser.parse_args()
    pid = os.getpid()
    with open('pretender-http.pid', 'w') as f:
        f.write(str(pid))
    # bottle.debug(True)
    run(args.host, args.port)
