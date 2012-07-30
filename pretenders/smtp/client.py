import json
from email.parser import Parser
try:
    # Python 3
    from io import StringIO
except ImportError:
    from StringIO import StringIO

from pretenders.base import get_logger
from pretenders.boss.client import BossClient
from pretenders.constants import FOREVER


LOGGER = get_logger('pretenders.smtp.client')


class SMTPMock(BossClient):

    boss_mock_type = 'smtp'
    mail_parser = Parser()

    def __init__(self, host, port):
        super(SMTPMock, self).__init__(host, port)
        self.preset.add('', times=FOREVER)

    def get_email(self, sequence_id=None):
        history = self.history.get(sequence_id)
        email_json = json.loads(history.read().decode('ascii'))  # fix encoding...
        email_data = email_json['data']
        LOGGER.debug(email_data)
        return self.mail_parser.parse(StringIO(email_data))

    def reset(self):
        super(SMTPMock, self).reset()
        self.preset.add('', times=FOREVER)
