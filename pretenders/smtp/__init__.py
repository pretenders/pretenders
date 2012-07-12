import json


class SMTPSerialiser(object):
    """
    Utility class to proxy SMTP data from mock to boss.

    It is used to serialise SMTP data as JSON data.
    """
    def __init__(self, **kwargs):
        self.data = kwargs

    def serialize(self):
        return json.dumps(self.data)
