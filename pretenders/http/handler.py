import datetime
import json

from pretenders.boss import HTTPPretenderModel


class HttpHandler(object):

    PRETENDERS = {}

    def new_pretender(self, uid, timeout):
        start = datetime.datetime.now()

        self.PRETENDERS[uid] = HTTPPretenderModel(
            start=start,
            timeout=datetime.timedelta(seconds=timeout),
            last_call=start,
            uid=uid,
        )

        return json.dumps({
            'path': "/mockhttp/{0}".format(uid),
            'id': uid})

    def delete_pretender(self, uid):
        "Delete a pretender by ``uid``"
        del self.PRETENDERS[uid]
