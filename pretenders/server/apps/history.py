import json
from collections import defaultdict

from bottle import delete, get, HTTPResponse

from pretenders.log import get_logger
from pretenders.server import app

LOGGER = get_logger('pretenders.server.apps.history')
HISTORY = defaultdict(list)


def save_history(uid, request):
    """
    Save a value in history
    """
    HISTORY[uid].append(request)


@app.get('/history/<uid:int>/<ordinal:int>')
def get_history(uid, ordinal):
    """
    Access requests issued to the mock server
    """
    try:
        return json.dumps(HISTORY[uid][ordinal])
    except IndexError:
        raise HTTPResponse(b"No recorded request", status=404)
    except Exception:
        LOGGER.exception('Unexpected exception')


@app.get('/history/<uid:int>')
def get_all_history(uid):
    """
    Access all requests issued to the mock server
    """
    try:
        return json.dumps(HISTORY[uid])
    except:
        LOGGER.exception('Unexpected exception')


@app.delete('/history/<uid:int>')
def clear_history(uid):
    """
    Delete all recorded requests
    """
    del HISTORY[uid][:]
