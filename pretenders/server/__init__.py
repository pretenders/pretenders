from os.path import join, dirname

import bottle
from .middleware import ExceptionLoggingMiddleware

bottle.TEMPLATE_PATH.insert(0, join(dirname(__file__), 'templates'))
app = bottle.Bottle()
app.catchall = False

pretender_app = ExceptionLoggingMiddleware(app)

# Import apps so that they get initialised for bottle.
from pretenders.server.apps import history, preset, replay, pretender  # NOQA
import pretenders.server.views  # NOQA
