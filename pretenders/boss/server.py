import datetime
import json
import logging
import os
import re
import signal
import subprocess
import sys
import time
try:
    from collections import OrderedDict
except ImportError:
    #2.6 compatibility
    from pretenders.compat.ordered_dict import OrderedDict

from bottle import request, response, HTTPResponse
from bottle import delete, get, post
from bottle import run as run_bottle

from pretenders.base import in_parent_process
from pretenders.boss import MockServer
from pretenders.constants import (
    RETURN_CODE_PORT_IN_USE,
    MOCK_PORT_RANGE,
    TIMEOUT_MOCK_SERVER)
from pretenders.http import Preset


LOGGER = logging.getLogger('pretenders.boss.server')
UID_COUNTER = 0
HTTP_MOCK_SERVERS = {}
REQUEST_ONLY_HEADERS = ['User-Agent', 'Connection', 'Host', 'Accept']
BOSS_PORT = None
presets = OrderedDict()
history = []


class NoPortAvailableException(Exception):
    pass


def acceptable_response_header(header):
    "Use to filter which HTTP headers in the request should be removed"
    return header not in REQUEST_ONLY_HEADERS


def to_dict(wsgi_headers, include=lambda _: True):
    """
    Convert WSGIHeaders to a dict so that it can be JSON-encoded
    """
    ret = {}
    for k, v in wsgi_headers.items():
        if include(k):
            ret[k] = v
    return ret


def get_header(header, default=None):
    return request.headers.get(header, default)


def pop_preset(preset_list, key):
    del preset_list[0]
    if not preset_list:
        del presets[key]


def select_preset(value):
    """
    Select a preset to respond with.

    Look through the presets for a match. If one is found pop off a preset
    response and return it.

    ``values`` is a tuple of values to match against the regexes stored in
    presets. They are assumed to be in the same sequence as those of the
    regexes.

    Return 404 if no preset found that matches.
    """
    for key, preset_list in presets.items():

        preset = preset_list[0]
        preset_matches = re.match(preset.rule, value)
        if preset_matches:
            pop_preset(preset_list, key)
            return preset

    raise HTTPResponse(b"No matching preset response", status=404)


@post('/mock/<uid:int>')
def replay(uid):
    """
    Replay a previously recorded preset, and save the request in history
    """
    # Make a note that this mock server is still in use.
    HTTP_MOCK_SERVERS[uid].keep_alive()

    if not len(presets):
        raise HTTPResponse(b"No preset response", status=404)
    mock_request = json.loads(request.body.read().decode('ascii'))
    history.append(mock_request)
    preset = select_preset(mock_request['match'])
    response.content_type = 'application/json'
    return preset.as_json()


@post('/preset')
def add_preset():
    """
    Save the incoming request body as a preset response
    """
    preset = Preset(json_data=request.body.read())
    rule = preset.rule
    if rule not in presets:
        presets[rule] = []
    url_presets = presets[rule]
    url_presets.append(preset)


@delete('/preset')
def clear_presets():
    """
    Delete all recorded presets
    """
    presets.clear()


@get('/history/<ordinal:int>')
def get_history(ordinal):
    """
    Access requests issued to the mock server
    """
    try:
        return json.dumps(history[ordinal])
    except IndexError:
        raise HTTPResponse(b"No recorded request", status=404)
    except Exception:
        LOGGER.exception('Unexpected exception')


@delete('/history')
def clear_history():
    """
    Delete all recorded requests
    """
    del history[:]


@post('/mock_server/http')
def create_http_mock():
    """
    Client is requesting an http mock instance.

    Launch an http mock instance on a random unused port.
    Keep track of the pid of the mock instance
    Kill the mock instance after timeout expired.
    Return the location of the mock instance.
    """
    global UID_COUNTER
    UID_COUNTER += 1
    uid = UID_COUNTER

    for port_number in MOCK_PORT_RANGE:
        process = subprocess.Popen([
            sys.executable,
            "-m",
            "pretenders.http.server",
            "-H", "localhost",
            "-p", str(port_number),
            "-b", str(BOSS_PORT),
            "-i", str(uid),
            ])
        time.sleep(2)  # Wait this long for failure
        process.poll()
        if process.returncode == RETURN_CODE_PORT_IN_USE:
            LOGGER.info("Return code already set. "
                        "Assuming failed due to socket error.")
            continue
        start = datetime.datetime.now()
        HTTP_MOCK_SERVERS[uid] = MockServer(
            start=start,
            port=port_number,
            pid=process.pid,
            timeout=datetime.timedelta(seconds=TIMEOUT_MOCK_SERVER),
            last_call=start,
            uid=uid,
        )
        return json.dumps({
            'url': "localhost:{0}".format(port_number),
            'id': uid})
    raise NoPortAvailableException("All ports in range in use")


@get('/mock_server/<uid:int>')
def get_http_mock(uid):
    response.content_type = 'application/json'
    try:
        return HTTP_MOCK_SERVERS[uid].as_json()
    except KeyError:
        raise HTTPResponse(b"No matching http mock", status=404)


@delete('/mock_server/http/<uid:int>')
def delete_http_mock(uid):
    "Delete http mock servers"
    delete_mock_server(uid)


@delete('/mock_server')
def view_delete_mock_server():
    "Delete an http mock"
    LOGGER.debug("Got DELETE request", request.GET)
    if request.GET.get('stale'):
        LOGGER.debug("Got request to delete stale mock servers")
        # Delete all stale requests
        now = datetime.datetime.now()
        for uid, server in HTTP_MOCK_SERVERS.copy().items():
            LOGGER.debug("Server: ", server)
            if server.last_call + server.timeout < now:
                LOGGER.info("Deleting server with UID: ", uid)
                delete_mock_server(uid)


def delete_mock_server(uid):
    "Delete a mock server by ``uid``"
    LOGGER.info("Performing delete on {0}".format(uid))
    pid = HTTP_MOCK_SERVERS[uid].pid
    LOGGER.info("attempting to kill pid {0}".format(pid))
    os.kill(pid, signal.SIGINT)
    del HTTP_MOCK_SERVERS[uid]


def run_maintainer():
    """
    Run the maintainer - pruning the number of mock servers running.

    :returns:
        The pid of the maintainer process.
    """
    process = subprocess.Popen([
            sys.executable,
            "-m",
            "pretenders.boss.maintain",
            "-H", "localhost",
            "-p", str(BOSS_PORT),
            ],
    )
    return process.pid


def run(host='localhost', port=8000):
    "Start the mock HTTP server"
    global BOSS_PORT
    BOSS_PORT = port
    if in_parent_process():
        run_maintainer()
    run_bottle(host=host, port=port, reloader=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Start the server')
    parser.add_argument('-H', '--host', dest='host', default='localhost',
                help='host/IP to run the server on (default: localhost)')
    parser.add_argument('-p', '--port', dest='port', type=int, default=8000,
                help='port number to run the server on (default: 8000)')

    args = parser.parse_args()
    pid = os.getpid()
    with open('pretender-http.pid', 'w') as f:
        f.write(str(pid))
    # bottle.debug(True)
    run(args.host, args.port)
