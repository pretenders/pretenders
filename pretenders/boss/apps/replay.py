import json

import bottle
from bottle import post, HTTPResponse

from pretenders.base import get_logger
from pretenders.boss.apps import pretender
from pretenders.boss.apps.history import save_history
from pretenders.boss.apps.preset import preset_count, select_preset

LOGGER = get_logger('pretenders.boss.apps.replay')


@post('/replay/<uid:int>')
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
    pretender.keep_alive(uid)

    if preset_count(uid) == 0:
        raise HTTPResponse(b"No preset response", status=404)
    mock_request = json.loads(bottle.request.body.read().decode('ascii'))
    LOGGER.debug('[UID:{0}] Saving history:\n{1}'.format(uid, mock_request))
    save_history(uid, mock_request)
    selected = select_preset(uid, mock_request['match'])
    bottle.response.content_type = 'application/json'
    return selected.as_json()
