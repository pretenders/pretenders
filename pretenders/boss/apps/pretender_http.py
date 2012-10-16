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
from pretenders.boss import HTTPPretenderModel

LOGGER = get_logger('pretenders.boss.apps.pretender_http')
UID_COUNTER = 0
HTTP_PRETENDERS = {}
"Dictionary containing details of currently active pretenders"


def keep_alive(uid):
    """
    Notification from a mock server that it must be kept  alive.
    """
    HTTP_PRETENDERS[uid].keep_alive()


@get('/http/<uid:int>')
def pretender_get(uid):
    bottle.response.content_type = 'application/json'
    try:
        return HTTP_PRETENDERS[uid].as_json()
    except KeyError:
        raise HTTPResponse(b"No matching http mock", status=404)


@post('/http')
def create_http_pretender():
    """
    Client is requesting a mock http instance.

    Generate a new UID for the pretender.
    Return the location of the pretender instance.
    """
    global UID_COUNTER
    UID_COUNTER += 1
    uid = UID_COUNTER

    post_body = bottle.request.body.read().decode('ascii')
    pretender_timeout = json.loads(post_body)['pretender_timeout']

    LOGGER.info("Creating http pretender access point at {0}".format(uid))

    start = datetime.datetime.now()

    HTTP_PRETENDERS[uid] = HTTPPretenderModel(
        start=start,
        timeout=datetime.timedelta(seconds=pretender_timeout),
        last_call=start,
        uid=uid,
    )

    return json.dumps({
        'path': "/mockhttp/{0}".format(uid),
        'id': uid})


def delete_http_pretender(uid):
    "Delete a pretender by ``uid``"
    LOGGER.info("Performing delete on http pretender {0}".format(uid))
    del HTTP_PRETENDERS[uid]


@delete('/http/<uid:int>')
def delete_http_mock(uid):
    "Delete http mock servers"
    delete_http_pretender(uid)


@delete('/http')
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
        for uid, server in HTTP_PRETENDERS.copy().items():
            LOGGER.debug("Pretender: {0}".format(server))
            if server.last_call + server.timeout < now:
                LOGGER.info("Deleting pretender with UID: {0}".format(uid))
                delete_http_pretender(uid)
