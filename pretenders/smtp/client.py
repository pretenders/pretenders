from pretenders.boss.client import BossClient
from pretenders.constants import FOREVER


class SMTPMock(BossClient):

    boss_mock_type = 'smtp'

    def __init__(self, host, port):
        super(SMTPMock, self).__init__(host, port)
        # fill presets...
        self.preset.add('', times=FOREVER)

    def get_email(self, sequence_id=None):
        history = self.history.get(sequence_id)
        return dict(history)
