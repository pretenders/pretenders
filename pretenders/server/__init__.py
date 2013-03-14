import bottle
from .middleware import ExceptionLoggingMiddleware

app = bottle.Bottle()
app.catchall = False

myapp = ExceptionLoggingMiddleware(app)

# Import apps so that they get initialised for bottle.
from pretenders.server.apps import history, preset, replay, pretender  # NOQA
