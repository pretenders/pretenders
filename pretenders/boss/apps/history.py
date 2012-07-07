import json

from bottle import delete, get, HTTPResponse

from pretenders.base import get_logger

LOGGER = get_logger('pretenders.boss.apps.history')
HISTORY = []


def save_history(request):
    """
    Save a value in history
    """
    HISTORY.append(request)


@get('/history/<ordinal:int>')
def get_history(ordinal):
    """
    Access requests issued to the mock server
    """
    try:
        return json.dumps(HISTORY[ordinal])
    except IndexError:
        raise HTTPResponse(b"No recorded request", status=404)
    except Exception:
        LOGGER.exception('Unexpected exception')


@delete('/history')
def clear_history():
    """
    Delete all recorded requests
    """
    del HISTORY[:]
