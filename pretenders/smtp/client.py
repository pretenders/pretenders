from pretenders.boss.client import BossClient
from pretenders.base import APIHelper


class SMTPMock(BossClient):

    boss_mock_type = 'smtp'

    def get_email(self, sequence_id=None):
        return dict(self.history.get(sequence_id))
