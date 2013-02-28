import datetime
import json

from pretenders.server.base import get_logger
from pretenders.mock_servers import PretenderModel

LOGGER = get_logger('pretenders.http.handler')


class HTTPPretenderModel(PretenderModel):

    def __init__(self, path, **kwargs):
        super(HTTPPretenderModel, self).__init__(**kwargs)
        self.path = path


class HttpHandler(object):

    PRETENDERS = {}
    PRETENDER_NAME_UID = {}

    def get_or_create_pretender(self, uid, timeout, name):
        start = datetime.datetime.now()
        if name in self.PRETENDER_NAME_UID:
            pretender = self.PRETENDERS[self.PRETENDER_NAME_UID[name]]
        else:
            if name:
                self.PRETENDER_NAME_UID[name] = uid
                path = "/mockhttp/{0}".format(name)
            else:
                path = "/mockhttp/{0}".format(uid)

            pretender = HTTPPretenderModel(
                start=start,
                timeout=datetime.timedelta(seconds=timeout),
                last_call=start,
                uid=uid,
                name=name,
                path=path
            )
            self.PRETENDERS[uid] = pretender

        return json.dumps({
            'path': pretender.path,
            'id': pretender.uid})

    def delete_pretender(self, uid):
        "Delete a pretender by ``uid``"
        try:
            del self.PRETENDER_NAME_UID[self.PRETENDERS[uid].name]
        except KeyError:
            pass
        del self.PRETENDERS[uid]
