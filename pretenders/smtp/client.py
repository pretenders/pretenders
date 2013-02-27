import json
from pretenders.boss.client import BossClient
from pretenders.constants import FOREVER
from pretenders.smtp import SMTPSerialiser


class SMTPMock(BossClient):

    boss_mock_type = 'smtp'

    def __init__(self, host, port):
        super(SMTPMock, self).__init__(host, port)
        self.preset.add('', times=FOREVER)

    @property
    def pretend_port(self):
        return int(self.pretend_access_point.split(':')[1])

    @property
    def pretend_access_point(self):
        return self.pretender_details['full_host']

    def get_emails(self):
        history = self.history.list().read()
        converted_history = json.loads(history.decode('ascii'))
        return [SMTPSerialiser(**dict_info) for dict_info in converted_history]

    def get_email(self, sequence_id):
        history_rep = self.history.get(sequence_id)
        if history_rep.code == 404:
            return None
        history = history_rep.read()
        email = SMTPSerialiser(**json.loads(history.decode('ascii')))
        return email

    def reset(self):
        super(SMTPMock, self).reset()
        self.preset.add('', times=FOREVER)
