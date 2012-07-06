import logging
import os
import signal
try:
    from collections import OrderedDict
except ImportError:
    #2.6 compatibility
    from pretenders.compat.ordered_dict import OrderedDict

LOGGER = logging.getLogger('pretenders.boss.data')


UID_COUNTER = 0
HTTP_MOCK_SERVERS = {}
BOSS_PORT = None
PRESETS = OrderedDict()
HISTORY = []


def pop_preset(preset_list, key):
    del preset_list[0]
    if not preset_list:
        del PRESETS[key]


def delete_mock_server(uid):
    "Delete a mock server by ``uid``"
    LOGGER.info("Performing delete on {0}".format(uid))
    pid = HTTP_MOCK_SERVERS[uid].pid
    LOGGER.info("attempting to kill pid {0}".format(pid))
    os.kill(pid, signal.SIGINT)
    del HTTP_MOCK_SERVERS[uid]
