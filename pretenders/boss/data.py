try:
    from collections import OrderedDict
except ImportError:
    #2.6 compatibility
    from pretenders.compat.ordered_dict import OrderedDict

from pretenders.base import get_logger

LOGGER = get_logger('pretenders.boss.data')


UID_COUNTER = 0
BOSS_PORT = None
PRESETS = OrderedDict()
HISTORY = []


def pop_preset(preset_list, key):
    del preset_list[0]
    if not preset_list:
        del PRESETS[key]
