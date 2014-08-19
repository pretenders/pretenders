import sys

from pretenders.server.log import get_logger
from bottle import html_escape

LOGGER = get_logger('pretenders.server.middleware')


class ExceptionLoggingMiddleware(object):
    """
    Middleware that logs exceptions raised by the server.
    """

    def __init__(self, app, *args, **kwargs):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except Exception:
            # This code is largely taken from ``def wsgi()`` in the bottle
            # code itself, but logs to the log file rather than writing to
            # environ['wsgi.errors']
            LOGGER.exception("Error processing request")
            err = '<h1>Critical error while processing request: %s</h1>' \
                  % html_escape(environ.get('PATH_INFO', '/'))
            environ['wsgi.errors'].write(err)
            headers = [('Content-Type', 'text/html; charset=UTF-8')]
            start_response('500 INTERNAL SERVER ERROR', headers,
                           sys.exc_info())

            return []
