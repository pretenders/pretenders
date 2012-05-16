from bottle import request, response, route, run, HTTPResponse
from bottle import delete, get, post


presets = []
history = []


def to_dict(wsgi_headers, include=lambda _: True):
    """
    Convert WSGIHeaders to a dict so that it can be JSON-encoded
    """
    return {k: v for k, v in wsgi_headers.items() if include(k)}


def get_header(header, default=None):
    return request.headers.get(header, default)


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
    preset = presets.pop(0)
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
        'body': request.body,
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
    run(host='localhost', port=port, reloader=True)


if __name__ == "__main__":
    run_bottle()
