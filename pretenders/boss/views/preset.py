import re

import bottle
from bottle import delete, post, HTTPResponse

from pretenders.base import get_logger
from pretenders.boss import data
from pretenders.http import Preset

LOGGER = get_logger('pretenders.boss.views.preset')


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
    for key, preset_list in data.PRESETS.items():

        preset = preset_list[0]
        preset_matches = re.match(preset.rule, value)
        if preset_matches:
            data.pop_preset(preset_list, key)
            return preset

    raise HTTPResponse(b"No matching preset response", status=404)


@post('/preset')
def add_preset():
    """
    Save the incoming request body as a preset response
    """
    preset = Preset(json_data=bottle.request.body.read())
    rule = preset.rule
    if rule not in data.PRESETS:
        data.PRESETS[rule] = []
    url_presets = data.PRESETS[rule]
    url_presets.append(preset)


@delete('/preset')
def clear_presets():
    """
    Delete all recorded presets
    """
    data.PRESETS.clear()
