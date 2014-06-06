import email as email_lib
from email.parser import Parser
import json

from pretenders.common.compat import ensure_is_python_string


class SMTPSerialiser(object):
    """
    Utility class to proxy SMTP data from mock to boss.

    It is used to serialise SMTP data as JSON data.
    """
    def __init__(self, **kwargs):
        self.data = kwargs
        email = ensure_is_python_string(self.data['data'])
        self.message = Parser().parsestr(email)

    def serialize(self):
        return json.dumps(self.data)

    def __getitem__(self, key):
        return self.message.__getitem__(key)

    @property
    def content(self):
        payload = self.message.get_payload(decode=True)
        return ensure_is_python_string(payload)

    @property
    def subject(self):
        subj = email_lib.header.decode_header(self.message['Subject'])[0][0]
        return ensure_is_python_string(subj)
