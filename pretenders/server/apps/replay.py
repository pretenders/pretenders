import json

import bottle
from bottle import HTTPResponse

from pretenders.common.http import Preset, RequestSerialiser
from pretenders.server.log import get_logger
from pretenders.server import app
from pretenders.server.apps import pretender
from pretenders.server.apps.history import save_history
from pretenders.server.apps.preset import preset_count, select_preset


LOGGER = get_logger('pretenders.server.apps.replay')


def replay(uid, body):
    "Save the request and replay response"
    mock_request = json.loads(body)
    LOGGER.debug('[UID:{0}] Saving history:\n{1}'.format(uid, mock_request))
    save_history(uid, mock_request)
    if preset_count(uid) == 0:
        LOGGER.error("Cannot find matching request\n{0}".format(body))
        raise HTTPResponse(b"No preset response", status=404)
    selected = select_preset(uid, mock_request)
    LOGGER.debug("SELECTED:\n{0}".format(selected))
    return selected


@app.post('/replay/<uid>')
def replay_smtp(uid):
    """
    Replay a previously recorded preset, and save the request in history.

    Update the mock server identified by ``uid``.

    :returns:
        An HTTP response
            * Status Code 200 containing json data found in preset.
            * Status Code 404 if there are no matching presets.
    """
    # Make a note that this mock server is still in use.
    pretender.keep_alive('smtp', uid)
    bottle.response.content_type = 'application/json'
    selected = replay(uid, bottle.request.body.read().decode('ascii'))
    return selected.as_json()


@app.route('/mockhttp/<path:path>', method='ANY')
def replay_http(path):
    """
    Replay a previously recorded preset, and save the request in history
    """
    uid = path.split('/')[0]
    url = path[len(uid):]
    pretender.exists_or_404('http', uid)
    request_info = RequestSerialiser(url, bottle.request)
    body = request_info.serialize()
    LOGGER.debug("KEEPING UID {0} ALIVE".format(uid))
    pretender.keep_alive('http', uid)

    boss_response = replay(uid, body)
    preset = Preset(boss_response.as_json().encode('ascii'))
    # ^ Any suggestions about what we can do here?
    # Preset expects a string like object that can be decoded.
    # in py3k that means a 'bytes' object. in py2.X that means a string.
    # So the above works, but it looks ugly - ideally we'd handle both in
    # Preset constructor.
    return preset.as_http_response(bottle.response)
