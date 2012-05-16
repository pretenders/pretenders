from bottle import request, response, route, run, HTTPResponse
from bottle import delete, get, post

PATH_MATCH = 0
INDEPENDENT_RESPONSES = 1
mode = PATH_MATCH
presets = []
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

    If the current mode is ``INDEPENDENT_RESPONSES`` pop the top preset and
    return it.

    Otherwise match the path and request method to pick the appropriate preset.

    Return 404 if no preset found that matches.
    Return 405 if no preset matches required method.
    """
    if mode == INDEPENDENT_RESPONSES:
        return presets.pop(0)
    else:
        path_match = False
        for preset in presets:
            preset_path = preset['match-path']
            preset_method = preset['match-method']
            if preset_path == path:
                if request.method == preset_method or preset_method == '*':
                    return preset
                else:
                    path_match = True

        if path_match:
            raise HTTPResponse(b"Path matched but invalid method", status=405)
        else:
            raise HTTPResponse(b"No matching preset response", status=404)


@post('/mode')
def set_mode():
    "Set the mode by which we select presets"
    global mode
    msg = request.body.read()
    if msg == b'path_match':
        mode = PATH_MATCH
    elif msg == b'independent_responses':
        mode = INDEPENDENT_RESPONSES


@route('/mock<path:path>', method='ANY')
def replay(path):
    """
    Replay a previously recorded preset, and save the request in history
    """
    if not len(presets):
        raise HTTPResponse(b"No preset response", status=404)
    saved_request = {
        'body': request.body.read(),
        'headers': to_dict(request.headers),
        'method': request.method,
        'path': path,
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
    presets.append({
        'headers': headers,
        'body': request.body.read(),
        'status': int(get_header('X-Pretend-Response-Status', 200)),
        'match-method': get_header('X-Pretend-Match-Method'),
        'match-path': get_header('X-Pretend-Match-Path'),
    })


@delete('/preset')
def clear_presets():
    """
    Delete all recorded presets
    """
    del presets[:]


@get('/history/<ordinal:int>')
def get_history(ordinal):
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


def run_bottle(port=8000):
    run(host='localhost', port=port)


if __name__ == "__main__":
    run_bottle()
