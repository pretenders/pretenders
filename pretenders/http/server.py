import json

from bottle import request, route, run, HTTPResponse
from bottle import delete, get, post


presets = []
history = []


def to_dict(wsgi_headers):
    """
    Convert WSGIHeaders to a dict so that it can be JSON-encoded
    """
    return {k: v for k, v in wsgi_headers.items()}


@route('/mock', method='ANY')
def replay():
    """
    Replay a previously recorded preset, and save the request in history
    """
    if not len(presets):
        raise HTTPResponse(b"No preset response", status=404)
    encoding = 'utf-8'  # find out proper value?
    saved_request = {
        'body': request.body.read().decode(encoding),
        'headers': to_dict(request.headers),
        'method': request.method,
        'path': request.path,
    }
    history.append(saved_request)
    body = presets.pop(0)
    return body


@post('/preset')
def add_preset():
    """
    Save the incoming request body as a preset response
    """
    # TODO: JSON decode in body, status, headers...
    presets.append(request.body)


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
        return json.dumps(saved_request)
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
