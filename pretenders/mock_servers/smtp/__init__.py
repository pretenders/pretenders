import json
from email.parser import Parser


class SMTPSerialiser(object):
    """
    Utility class to proxy SMTP data from mock to boss.

    It is used to serialise SMTP data as JSON data.
    """
    def __init__(self, **kwargs):
        self.data = kwargs
        email = self.data['data']
        if not isinstance(email, str):
            # Python2.6's version of the email parser doesn't like when these
            # come in as unicode. In Python 3 strings ARE sequences of unicode
            # characters, so I can only assume that the email parser has been
            # updated to handle them.
            email = str(email)
        self.message = Parser().parsestr(email)

    def serialize(self):
        return json.dumps(self.data)

    def __getitem__(self, key):
        return self.message.__getitem__(key)

    @property
    def content(self):
        return self.message.get_payload()
