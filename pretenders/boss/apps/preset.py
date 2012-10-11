import re
import time

import bottle
from bottle import delete, post, HTTPResponse

try:
    from collections import OrderedDict
except ImportError:
    #2.6 compatibility
    from pretenders.compat.ordered_dict import OrderedDict

from collections import defaultdict

from pretenders.base import get_logger
from pretenders.constants import FOREVER
from pretenders.http import Preset


LOGGER = get_logger('pretenders.boss.apps.preset')
PRESETS = defaultdict(OrderedDict)


def preset_count(uid):
    """
    Check whether there are any presets.
    """
    return len(PRESETS[uid])


def select_preset(uid, request):
    """
    Select a preset to respond with.

    Look through the presets for a match. If one is found pop off a preset
    response and return it.

    :param uid: The uid to look up presets for
    :param request: A dictionary representign the mock request. The 'value' item
        is used to match against the regexes stored in presets. They are assumed 
        to be in the same sequence as those of the regexes.

    Return 404 if no preset found that matches.

    If the preset is configured with an 'ETag' header then we check the request
    for an 'If-None-Match' header.  If the 'If-None-Match' header exists and 
    matches the value set in the preset then we return a 304 - Not Modified 
    otherwise the preset response is returned.

    If the preset is configured with a 'Last-Modified' header then we check the
    request for an 'If-Modified-Since' header.  If an 'If-Modified-Since' header
    exists and precedes the preset's 'Last-Modified' value then we return 
    304 Not Modified.
    """
    preset_dict = PRESETS[uid]
    for key, preset_list in preset_dict.items():

        preset = preset_list[0]
        preset_matches = re.match(preset.rule, request['match'])
        if preset_matches:

            if 'ETag' in preset.headers.keys():
                if_none_match = request['headers'].get('If-None-Match', None)
                if if_none_match and if_none_match == preset.headers['ETag']:
                    raise HTTPResponse(b"", status=304)

            if 'Last-Modified' in preset.headers.keys():
                if_modified_since = request['headers'].get(
                    'If-Modified-Since', None)
                if if_modified_since and is_modified(
                        preset.headers['Last-Modified'], if_modified_since):
                    raise HTTPResponse(b"", status=304)

            knock_off_preset(preset_dict, key)
            return preset

    raise HTTPResponse(b"No matching preset response", status=404)


def is_modified(last_modified, if_modified_since):
    """ 
    Returns True if a resource has been modified.
    Both last_modified and if_modified_since parameters are expected to be
    in standard HTTP date format eg Tue, 15 Nov 1994 12:45:26 GMT.
    """
    fmt = "%a, %d %b %Y %H:%M:%S %Z"
    return time.strptime(if_modified_since, fmt) > time.strptime(last_modified, fmt)


def knock_off_preset(preset_dict, key):
    """Knock a count off the preset at in list ``key`` within ``preset_dict``.

    Reduces the ``times`` paramter of a preset.
    Once the ``times`` reduces to zero it is removed.
    If ``times`` is ``FOREVER`` nothing happens.

    :param preset_dict:
        A dictionary containing preset dictionaries specific for a uid.

    :param key:
        The key pointing to the list to look up and pop an item from.
    """
    preset = preset_dict[key][0]
    if preset.times == FOREVER:
        return
    elif preset.times > 0:
        preset.times -= 1

    if preset.times == 0:
        del preset_dict[key][0]
        if not preset_dict[key]:
            del preset_dict[key]


@post('/preset/<uid:int>')
def add_preset(uid):
    """
    Save the incoming request body as a preset response
    """
    preset = Preset(json_data=bottle.request.body.read())
    if preset.times != FOREVER and preset.times <= 0:
        raise HTTPResponse(("Preset has {0} times. Must be greater than "
                             "zero.".format(preset.times).encode()),
                           status=400)

    rule = preset.rule
    if rule not in PRESETS[uid]:
        PRESETS[uid][rule] = []
    url_presets = PRESETS[uid][rule]
    url_presets.append(preset)


@delete('/preset/<uid:int>')
def clear_presets(uid):
    """
    Delete all recorded presets
    """
    PRESETS[uid].clear()
