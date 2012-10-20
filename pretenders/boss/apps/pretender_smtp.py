import datetime
import json
import os
import signal
import subprocess
import sys
import time

import bottle
from bottle import delete, get, post, HTTPResponse

from pretenders.base import get_logger
from pretenders.boss import SMTPPretenderModel
from pretenders.constants import (
    RETURN_CODE_PORT_IN_USE,
    PRETEND_PORT_RANGE)
from pretenders.boss import data
from pretenders.exceptions import NoPortAvailableException


LOGGER = get_logger('pretenders.boss.apps.pretender_smtp')
UID_COUNTER = 0
SMTP_PRETENDERS = {}
"Dictionary containing details of currently active pretenders"


def available_ports():
    "Get a set of ports available for starting pretenders"
    ports_in_use = set(map(lambda x: x.port, SMTP_PRETENDERS.values()))
    available_set = PRETEND_PORT_RANGE.difference(ports_in_use)
    return available_set


def keep_alive(uid):
    """
    Notification from a mock server that it must be kept  alive.
    """
    SMTP_PRETENDERS[uid].keep_alive()


@get('/smtp/<uid:int>')
def pretender_get(uid):
    bottle.response.content_type = 'application/json'
    try:
        return SMTP_PRETENDERS[uid].as_json()
    except KeyError:
        raise HTTPResponse(b"No matching http mock", status=404)


@post('/smtp')
def create_smtp_pretender():
    """
    Client is requesting a mock smtp instance.

    Launch an smtp pretender on a random unused port.
    Keep track of the pid of the pretender
    Kill the pretender instance after timeout expired.
    Return the location of the pretender instance.
    """
    global UID_COUNTER
    UID_COUNTER += 1
    uid = UID_COUNTER

    post_body = bottle.request.body.read().decode('ascii')
    pretender_timeout = json.loads(post_body)['pretender_timeout']

    for port_number in available_ports():
        LOGGER.info("Attempt to start smtp pretender on port {0}".format(
            port_number))
        process = subprocess.Popen([
            sys.executable,
            "-m",
            "pretenders.smtp.server",
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
        SMTP_PRETENDERS[uid] = SMTPPretenderModel(
            start=start,
            port=port_number,
            pid=process.pid,
            timeout=datetime.timedelta(seconds=pretender_timeout),
            last_call=start,
            uid=uid,
        )
        LOGGER.info("Started smtp pretender on port {0}".format(
            port_number))
        return json.dumps({
            'full_host': "localhost:{0}".format(port_number),
            'id': uid})
    raise NoPortAvailableException("All ports in range in use")


def delete_smtp_pretender(uid):
    "Delete a pretender by ``uid``"
    LOGGER.info("Performing delete on {0}".format(uid))
    pid = SMTP_PRETENDERS[uid].pid
    LOGGER.info("attempting to kill pid {0}".format(pid))
    try:
        os.kill(pid, signal.SIGKILL)
        del SMTP_PRETENDERS[uid]
    except OSError as e:
        LOGGER.info("OSError while killing:\n{0}".format(dir(e)))


@delete('/smtp')
def pretender_delete():
    """
    Delete pretenders with filters

    Currently only supports ``stale`` argument which deletes all those that
    have not had a request made in a period longer than the time out set on
    creation.
    """
    LOGGER.debug("Got DELETE request: {0}".format(bottle.request.GET))
    if bottle.request.GET.get('stale'):
        LOGGER.debug("Got request to delete stale pretenders")
        # Delete all stale requests
        now = datetime.datetime.now()
        for uid, server in SMTP_PRETENDERS.copy().items():
            LOGGER.debug("Pretender: {0}".format(server))
            if server.last_call + server.timeout < now:
                LOGGER.info("Deleting pretender with UID: {0}".format(uid))
                delete_smtp_pretender(uid)
