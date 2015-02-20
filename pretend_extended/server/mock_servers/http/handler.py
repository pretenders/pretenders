import datetime
import json

from pretend_extended.common.constants import FOREVER
from pretend_extended.server.log import get_logger
from pretend_extended.server.mock_servers import PretenderModel

LOGGER = get_logger('pretend_extended.http.handler')


class HTTPPretenderModel(PretenderModel):

    def __init__(self, path, **kwargs):
        super(HTTPPretenderModel, self).__init__(protocol='http', **kwargs)
        self.path = path


class HttpHandler(object):

    PRETENDERS = {}

    def get_or_create_pretender(self, name, timeout):
        start = datetime.datetime.now()
        if name in self.PRETENDERS:
            pretender = self.PRETENDERS[name]
        else:
            path = "/mockhttp/{0}".format(name) if name != 'global' else '/'

            if timeout != FOREVER:
                timeout = datetime.timedelta(seconds=timeout)

            pretender = HTTPPretenderModel(
                start=start,
                timeout=timeout,
                last_call=start,
                name=name,
                path=path
            )
            self.PRETENDERS[name] = pretender

        return json.dumps({
            'path': pretender.path,
            'id': pretender.name})

    def delete_pretender(self, name):
        "Delete a pretender by ``name``"
        del self.PRETENDERS[name]
