import datetime
import json

import bottle
from bottle import delete, get, post, HTTPResponse

from pretenders import settings
from pretenders.base import get_logger


LOGGER = get_logger('pretenders.boss.apps.pretender')
UID_COUNTER = 0
"Dictionary containing details of currently active pretenders"
PRETENDERS = {
    'http': {},
    'smtp': {},
}


from pretenders.boss import HTTPPretenderModel


class HttpHandler(object):

    def new_pretender(self, uid, timeout):
        start = datetime.datetime.now()

        PRETENDERS['http'][uid] = HTTPPretenderModel(
            start=start,
            timeout=datetime.timedelta(seconds=timeout),
            last_call=start,
            uid=uid,
        )

        return json.dumps({
            'path': "/mockhttp/{0}".format(uid),
            'id': uid})

    def delete_pretender(self, uid):
        "Delete a pretender by ``uid``"
        del PRETENDERS['http'][uid]


import os
import signal
import subprocess
import sys
import time
from pretenders.boss import SMTPPretenderModel
from pretenders.constants import (
    RETURN_CODE_PORT_IN_USE,
    PRETEND_PORT_RANGE
)
from pretenders.boss import data
from pretenders.exceptions import NoPortAvailableException


class SmtpHandler(object):

    def available_ports(self):
        """
        Get a set of ports available for starting pretenders
        """
        ports_in_use = set(map(lambda x: x.port, PRETENDERS['smtp'].values()))
        available_set = PRETEND_PORT_RANGE.difference(ports_in_use)
        return available_set

    def new_pretender(self, uid, timeout):
        """
        Launch a new SMTP pretender in a separate process.

        It will first look for an available port.
        """
        for port_number in self.available_ports():
            LOGGER.info(
                "Attempt to start smtp pretender on port {0}, timeout {1}"
                .format(port_number, timeout))
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
            PRETENDERS['smtp'][uid] = SMTPPretenderModel(
                start=start,
                port=port_number,
                pid=process.pid,
                timeout=datetime.timedelta(seconds=timeout),
                last_call=start,
                uid=uid,
            )
            LOGGER.info("Started smtp pretender on port {0}".format(
                port_number))
            return json.dumps({
                'full_host': "localhost:{0}".format(port_number),
                'id': uid})
        raise NoPortAvailableException("All ports in range in use")

    def delete_pretender(self, uid):
        "Delete a pretender by ``uid``"
        LOGGER.info("Performing delete on {0}".format(uid))
        pid = PRETENDERS['smtp'][uid].pid
        LOGGER.info("attempting to kill pid {0}".format(pid))
        try:
            os.kill(pid, signal.SIGKILL)
            del PRETENDERS['smtp'][uid]
        except OSError as e:
            LOGGER.info("OSError while killing:\n{0}".format(dir(e)))


HANDLERS = {
    'http': HttpHandler(),
    'smtp': SmtpHandler(),
}


def keep_alive(uid, protocol):
    """
    Notification from a mock server that it must be kept  alive.
    """
    PRETENDERS[protocol][uid].keep_alive()


@get('/<protocol>/<uid:int>')
def pretender_get(protocol, uid):
    bottle.response.content_type = 'application/json'
    try:
        return PRETENDERS[protocol][uid].as_json()
    except KeyError:
        raise HTTPResponse(b"No matching {0} mock".format(protocol),
                           status=404)


@post('/<protocol>')
def create_pretender(protocol):
    """
    Client is requesting a mock instance for the given protocol.

    Generate a new UID for the pretender.
    Return the location of the pretender instance.

    Instance creation is protocol-dependent. For HTTP the same boss
    server will act as pretender in a given sub-URL. For other
    protocols, new processes may be spawn and listen on different
    ports.
    """
    global UID_COUNTER
    UID_COUNTER += 1
    uid = UID_COUNTER

    post_body = bottle.request.body.read().decode('ascii')
    body_data = json.loads(post_body)
    timeout = body_data.get('pretender_timeout', settings.TIMEOUT_PRETENDER)

    LOGGER.info("Creating {0} pretender access point at {1}"
                .format(protocol, uid))
    return HANDLERS[protocol].new_pretender(uid, timeout)


@delete('/<protocol>/<uid:int>')
def delete_http_mock(protocol, uid):
    "Delete http mock servers"
    LOGGER.info("Performing delete on {0} pretender {1}"
                .format(protocol, uid))
    HANDLERS[protocol].delete_pretender(uid)


@delete('/<protocol>')
def pretender_delete(protocol):
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
        for uid, server in PRETENDERS[protocol].copy().items():
            LOGGER.debug("Pretender: {0}".format(server))
            if server.last_call + server.timeout < now:
                LOGGER.info("Deleting pretender with UID: {0}".format(uid))
                HANDLERS[protocol].delete_pretender(uid)
