import json

import bottle
from bottle import post, HTTPResponse

from pretenders.base import get_logger
from pretenders.boss import data
from pretenders.boss.views.preset import select_preset

LOGGER = get_logger('pretenders.boss.views.mock')


@post('/mock/<uid:int>')
def replay(uid):
    """
    Replay a previously recorded preset, and save the request in history
    """
    # Make a note that this mock server is still in use.
    data.HTTP_MOCK_SERVERS[uid].keep_alive()

    if not len(data.PRESETS):
        raise HTTPResponse(b"No preset response", status=404)
    mock_request = json.loads(bottle.request.body.read().decode('ascii'))
    data.HISTORY.append(mock_request)
    selected = select_preset(mock_request['match'])
    bottle.response.content_type = 'application/json'
    return selected.as_json()
