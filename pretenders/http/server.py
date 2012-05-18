import re
from collections import OrderedDict

from bottle import request, response, route, HTTPResponse
from bottle import delete, get, post
from bottle import run as run_bottle

presets = OrderedDict()
history = []


def to_dict(wsgi_headers, include=lambda _: True):
    """
    Convert WSGIHeaders to a dict so that it can be JSON-encoded
    """
    return {k: v for k, v in wsgi_headers.items() if include(k)}


def get_header(header, default=None):
    return request.headers.get(header, default)


def select_preset(path):
    """Select a preset to respond with.

    Look through the presets for a match. If one is found pop off a preset
    response and return it.

    Return 404 if no preset found that matches.
    Return 405 if no preset matches required method.
    """
    path_match = False
    for key, preset_list in presets.items():
        preset = preset_list[0]
        preset_path = preset['match-path']
        preset_method = preset['match-method']
        if re.match(preset_path, path):
            if re.match(preset_method, request.method):
                del preset_list[0]
                if not preset_list:
                    del presets[key]
                return preset
            else:
                path_match = True

    if path_match:
        raise HTTPResponse(b"Path matched but invalid method", status=405)
    else:
        raise HTTPResponse(b"No matching preset response", status=404)


@route('/mock<path:path>', method='ANY')
def replay(path):
    """
    Replay a previously recorded preset, and save the request in history
    """
    if not len(presets):
        raise HTTPResponse(b"No preset response", status=404)
    relative_url = path
    if request.query_string:
        relative_url = "{0}?{1}".format(relative_url, request.query_string)
    saved_request = {
        'body': request.body.read(),
        'headers': to_dict(request.headers),
        'method': request.method,
        'path': relative_url,
    }
    history.append(saved_request)

    preset = select_preset(path)

    for header, value in preset['headers'].items():
        response.set_header(header, value)
    response.status = preset['status']
    return preset['body']


@post('/preset')
def add_preset():
    """
    Save the incoming request body as a preset response
    """
    headers = to_dict(request.headers,
                      include=lambda x: not x.startswith('X-Pretend-'))

    method = get_header('X-Pretend-Match-Method', '')
    path = get_header('X-Pretend-Match-Path', '')

    if (path, method) not in presets:
        presets[(path, method)] = []

    path_presets = presets[(path, method)]
    path_presets.append({
        'headers': headers,
        'body': request.body.read(),
        'status': int(get_header('X-Pretend-Response-Status', 200)),
        'match-method': method,
        'match-path': path,
    })


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
            response.set_header(header, value)
        response.set_header('X-Pretend-Request-Method', saved['method'])
        response.set_header('X-Pretend-Request-Path', saved['path'])
        return saved['body']
    except IndexError:
        raise HTTPResponse(b"No recorded request", status=404)


@delete('/history')
def clear_history():
    """
    Delete all recorded requests
    """
    del history[:]


def run(port=8000):
    "Start the mock HTTP server"
    run_bottle(host='localhost', port=port, reloader=True)


if __name__ == "__main__":
    run()
