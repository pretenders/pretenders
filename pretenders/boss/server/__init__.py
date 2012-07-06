import json
import logging

import bottle
from bottle import post, HTTPResponse

from pretenders.base import in_parent_process, save_pid_file, setup_logging
from pretenders.boss.server import data
from pretenders.boss.server.preset import select_preset
from pretenders.boss.server.utils import run_maintainer
# Import views so that they get initialised for bottle.
from pretenders.boss.server import history, mock_server, preset

LOGGER = logging.getLogger('pretenders.boss.server')


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
    preset = select_preset(mock_request['match'])
    bottle.response.content_type = 'application/json'
    return preset.as_json()


def run(host='localhost', port=8000):
    "Start the mock HTTP server"
    data.BOSS_PORT = port
    setup_logging()
    if in_parent_process():
        run_maintainer()
        save_pid_file('pretenders-boss.pid')
    bottle.run(host=host, port=port, reloader=True)
