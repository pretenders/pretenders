import datetime
import json
import logging
import subprocess
import sys
import time

import bottle
from bottle import delete, get, post, HTTPResponse

from pretenders.exceptions import NoPortAvailableException
from pretenders.boss import MockServer
from pretenders.boss.server import data
from pretenders.boss.server.utils import delete_mock_server
from pretenders.constants import (
    RETURN_CODE_PORT_IN_USE,
    MOCK_PORT_RANGE)


LOGGER = logging.getLogger('pretenders.boss.server.mock_server')


@post('/mock_server/http')
def create_http_mock():
    """
    Client is requesting an http mock instance.

    Launch an http mock instance on a random unused port.
    Keep track of the pid of the mock instance
    Kill the mock instance after timeout expired.
    Return the location of the mock instance.
    """
    data.UID_COUNTER += 1
    uid = data.UID_COUNTER

    post_body = bottle.request.body.read().decode('ascii')

    mock_timeout = json.loads(post_body)['mock_timeout']

    for port_number in MOCK_PORT_RANGE:
        process = subprocess.Popen([
            sys.executable,
            "-m",
            "pretenders.http.server",
            "-H", "localhost",
            "-p", str(port_number),
            "-b", str(data.BOSS_PORT),
            "-i", str(uid),
            ])
        time.sleep(2)  # Wait this long for failure
        process.poll()
        if process.returncode == RETURN_CODE_PORT_IN_USE:
            LOGGER.info("Return code already set. "
                        "Assuming failed due to socket error.")
            continue
        start = datetime.datetime.now()
        data.HTTP_MOCK_SERVERS[uid] = MockServer(
            start=start,
            port=port_number,
            pid=process.pid,
            timeout=datetime.timedelta(seconds=mock_timeout),
            last_call=start,
            uid=uid,
        )
        return json.dumps({
            'url': "localhost:{0}".format(port_number),
            'id': uid})
    raise NoPortAvailableException("All ports in range in use")


@get('/mock_server/<uid:int>')
def mock_server_get(uid):
    bottle.response.content_type = 'application/json'
    try:
        return data.HTTP_MOCK_SERVERS[uid].as_json()
    except KeyError:
        raise HTTPResponse(b"No matching http mock", status=404)


@delete('/mock_server/http/<uid:int>')
def delete_http_mock(uid):
    "Delete http mock servers"
    delete_mock_server(uid)


@delete('/mock_server')
def mock_server_delete():
    "Delete an http mock"
    LOGGER.debug("Got DELETE request: {0}".format(bottle.request.GET))
    if bottle.request.GET.get('stale'):
        LOGGER.debug("Got request to delete stale mock servers")
        # Delete all stale requests
        now = datetime.datetime.now()
        for uid, server in data.HTTP_MOCK_SERVERS.copy().items():
            LOGGER.debug("Server: {0}".format(server))
            if server.last_call + server.timeout < now:
                LOGGER.info("Deleting server with UID: {0}".format(uid))
                delete_mock_server(uid)
