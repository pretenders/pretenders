import json

import bottle
from bottle import post, HTTPResponse, route

from pretenders.base import get_logger
from pretenders.boss.apps import pretender
from pretenders.boss.apps.history import save_history
from pretenders.boss.apps.preset import preset_count, select_preset
from pretenders.http import Preset, RequestSerialiser
from pretenders.http.handler import HttpHandler


LOGGER = get_logger('pretenders.boss.apps.replay')


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


@post('/replay/<uid:int>')
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


@route('/mockhttp/<uid:int><url:path>', method='ANY')
def replay_http(uid, url):
    """
    Replay a previously recorded preset, and save the request in history
    """

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


@route('/mockhttp/<name><url:path>', method='ANY')
def replay_http_by_name(name, url):
    try:
        uid = HttpHandler().PRETENDER_NAME_UID[name]
    except KeyError:
        raise HTTPResponse("No matching mock by that name '{0}"
                           .format(name).encode(),
                           status=404)
    return replay_http(uid, url)
