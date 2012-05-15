from bottle import request, response, route, run, HTTPResponse
from bottle import delete, get, post


presets = []
history = []


def to_dict(wsgi_headers):
    """
    Convert WSGIHeaders to a dict so that it can be JSON-encoded
    """
    return {k: v for k, v in wsgi_headers.items()}


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
    headers = {
        k: v for k, v in request.headers.items()
        if not k.startswith('X-Pretend-')
    }
    presets.append({
        'body': request.body,
        'status': int(request.headers.get('X-Pretend-Response-Status', 200)),
        'headers': headers,
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
        saved_request = history[ordinal]
        for header, value in saved_request['headers'].items():
            response.set_header(header, value)
        response.set_header('X-Pretend-Request-Method', saved_request['method'])
        response.set_header('X-Pretend-Request-Path', saved_request['path'])
        return saved_request['body']
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
