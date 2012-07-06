try:
    from collections import OrderedDict
except ImportError:
    #2.6 compatibility
    from pretenders.compat.ordered_dict import OrderedDict


UID_COUNTER = 0
HTTP_MOCK_SERVERS = {}
REQUEST_ONLY_HEADERS = ['User-Agent', 'Connection', 'Host', 'Accept']
BOSS_PORT = None
PRESETS = OrderedDict()
HISTORY = []
