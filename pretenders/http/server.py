import re
import traceback
from collections import OrderedDict

import bottle
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
    return {k: v for k, v in wsgi_headers.items() if include(k)}


def get_header(header, default=None):
    return request.headers.get(header, default)


def select_preset(url):
    """Select a preset to respond with.

    Look through the presets for a match. If one is found pop off a preset
    response and return it.

    Return 404 if no preset found that matches.
    Return 405 if no preset matches required method.
    """
    url_match = False
    for key, preset_list in presets.items():
        preset = preset_list[0]
        preset_url = preset['match-url']
        preset_method = preset['match-method']
        if re.match(preset_url, url):
            if re.match(preset_method, request.method):
                del preset_list[0]
                if not preset_list:
                    del presets[key]
                return preset
            else:
                url_match = True

    if url_match:
        raise HTTPResponse(b"URL matched but invalid method", status=405)
    else:
        raise HTTPResponse(b"No matching preset response", status=404)


@route('/mock<url:path>', method='ANY')
def replay(url):
    """
    Replay a previously recorded preset, and save the request in history
    """
    if not len(presets):
        raise HTTPResponse(b"No preset response", status=404)
    relative_url = url
    if request.query_string:
        relative_url = "{0}?{1}".format(relative_url, request.query_string)
    saved_request = {
        'body': request.body.read(),
        'headers': to_dict(request.headers),
        'method': request.method,
        'url': relative_url,
    }
    history.append(saved_request)
    # print(saved_request)

    preset = select_preset(url)

    for header, value in preset['headers'].items():
        response.set_header(header, value)
    response.status = preset['status']
    return preset['body']



@post('/preset')
def add_preset():
    """
    Save the incoming request body as a preset response
    """
    headers = to_dict(request.headers, include=acceptable_response_header)

    method = get_header('X-Pretend-Match-Method', '')
    url = get_header('X-Pretend-Match-Url', '')

    if (url, method) not in presets:
        presets[(url, method)] = []

    url_presets = presets[(url, method)]
    new_preset = {
        'headers': headers,
        'body': request.body.read(),
        'status': int(get_header('X-Pretend-Response-Status', 200)),
        'match-method': method,
        'match-url': url,
    }
    url_presets.append(new_preset)
    # print('New preset: {0}'.format(new_preset))


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
    except Exception as e:
        # print('Exception: {0}'.format(e))
        traceback.print_exc()


@delete('/history')
def clear_history():
    """
    Delete all recorded requests
    """
    del history[:]


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
