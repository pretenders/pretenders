import datetime
import json

from pretenders.log import get_logger
from pretenders.mock_servers import PretenderModel

LOGGER = get_logger('pretenders.http.handler')


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
            path = "/mockhttp/{0}".format(name)

            pretender = HTTPPretenderModel(
                start=start,
                timeout=datetime.timedelta(seconds=timeout),
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
