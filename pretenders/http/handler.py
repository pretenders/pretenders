import datetime
import json

from pretenders.boss import PretenderModel
from pretenders.exceptions import DuplicateNameException


class HTTPPretenderModel(PretenderModel):
    pass


class HttpHandler(object):

    PRETENDERS = {}
    PRETENDER_NAME_UID = {}

    def new_pretender(self, uid, timeout, name):
        start = datetime.datetime.now()
        if name in self.PRETENDER_NAME_UID:
            raise DuplicateNameException("Name '{0}' already exists as uid {1}"
                                         .format(name, uid))

        self.PRETENDERS[uid] = HTTPPretenderModel(
            start=start,
            timeout=datetime.timedelta(seconds=timeout),
            last_call=start,
            uid=uid,
            name=name
        )
        if name:
            self.PRETENDER_NAME_UID[name] = uid
            path = "/mockhttp/{0}".format(name)
        else:
            path = "/mockhttp/{0}".format(uid)

        return json.dumps({
            'path': path,
            'id': uid})

    def delete_pretender(self, uid):
        "Delete a pretender by ``uid``"
        try:
            del self.PRETENDER_NAME_UID[self.PRETENDERS[uid].name]
        except KeyError:
            pass
        del self.PRETENDERS[uid]
