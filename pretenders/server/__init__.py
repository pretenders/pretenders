import bottle

app = bottle.Bottle()


# Import apps so that they get initialised for bottle.
from pretenders.server.apps import history, preset, replay, pretender  # NOQA
