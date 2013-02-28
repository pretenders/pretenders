import json
from email.parser import Parser


class SMTPSerialiser(object):
    """
    Utility class to proxy SMTP data from mock to boss.

    It is used to serialise SMTP data as JSON data.
    """
    def __init__(self, **kwargs):
        self.data = kwargs
        self.message = Parser().parsestr(self.data['data'])

    def serialize(self):
        return json.dumps(self.data)

    def __getitem__(self, key):
        return self.message.__getitem__(key)

    @property
    def content(self):
        return self.message.get_payload()
