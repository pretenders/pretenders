import re

import bottle
from bottle import delete, post, HTTPResponse

try:
    from collections import OrderedDict
except ImportError:
    #2.6 compatibility
    from pretenders.compat.ordered_dict import OrderedDict

from collections import defaultdict
from pretenders.base import get_logger
from pretenders.http import Preset

LOGGER = get_logger('pretenders.boss.views.preset')
PRESETS = defaultdict(OrderedDict)


def preset_count(uid):
    """
    Check whether there are any presets.
    """
    return len(PRESETS[uid])


def select_preset(uid, value):
    """
    Select a preset to respond with.

    Look through the presets for a match. If one is found pop off a preset
    response and return it.

    ``values`` is a tuple of values to match against the regexes stored in
    presets. They are assumed to be in the same sequence as those of the
    regexes.

    Return 404 if no preset found that matches.
    """
    preset_dict = PRESETS[uid]
    for key, preset_list in preset_dict.items():

        preset = preset_list[0]
        preset_matches = re.match(preset.rule, value)
        if preset_matches:
            pop_preset(preset_dict, key)
            return preset

    raise HTTPResponse(b"No matching preset response", status=404)


def pop_preset(preset_dict, key):
    """Pop a preset in the list at ``key`` within ``preset_dict``.

    :param preset_dict:
        A dictionary containing preset dictionaries specific for a uid.

    :param key:
        The key pointing to the list to look up and pop an item from.
    """
    del preset_dict[key][0]
    if not preset_dict[key]:
        del preset_dict[key]


@post('/preset/<uid:int>')
def add_preset(uid):
    """
    Save the incoming request body as a preset response
    """
    preset = Preset(json_data=bottle.request.body.read())
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
