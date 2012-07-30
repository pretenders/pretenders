import json
from pretenders.boss.client import BossClient
from pretenders.constants import FOREVER


class SMTPMock(BossClient):

    boss_mock_type = 'smtp'

    def __init__(self, host, port):
        super(SMTPMock, self).__init__(host, port)
        self.preset.add('', times=FOREVER)

    def get_email(self, sequence_id=None):
        history = self.history.get(sequence_id)
        email = json.loads(history.read().decode('ascii'))  # fix encoding...
        return email

    def reset(self):
        super(SMTPMock, self).reset()
        self.preset.add('', times=FOREVER)
