import json

import bottle
from bottle import post, HTTPResponse

from pretenders.base import get_logger
from pretenders.boss.views import mock_server
from pretenders.boss.views.history import save_history
from pretenders.boss.views.preset import preset_count, select_preset

LOGGER = get_logger('pretenders.boss.views.mock')


@post('/mock/<uid:int>')
def replay(uid):
    """
    Replay a previously recorded preset, and save the request in history.

    Update the mock server identified by ``uid``.

    :returns:
        An HTTP response
            * Status Code 200 containing json data found in preset.
            * Status Code 404 if there are no matching presets.
    """
    # Make a note that this mock server is still in use.
    mock_server.keep_alive(uid)

    if preset_count(uid) == 0:
        raise HTTPResponse(b"No preset response", status=404)
    mock_request = json.loads(bottle.request.body.read().decode('ascii'))
    save_history(uid, mock_request)
    selected = select_preset(uid, mock_request['match'])
    bottle.response.content_type = 'application/json'
    return selected.as_json()
