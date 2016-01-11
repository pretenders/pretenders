import json
from pretenders.client import BossClient
from pretenders.common.smtp import SMTPSerialiser


class SMTPMock(BossClient):

    boss_mock_type = 'smtp'

    def __init__(self, host, port):
        super(SMTPMock, self).__init__(host, port)

    @property
    def pretend_port(self):
        return int(self.pretend_access_point.split(':')[1])

    @property
    def pretend_access_point(self):
        return self.pretender_details['full_host']

    def get_emails(self):
        history_resp, history = self.history.list()
        converted_history = json.loads(history.decode('ascii'))
        return [SMTPSerialiser(**dict_info) for dict_info in converted_history]

    def get_email(self, sequence_id):
        history_resp, history = self.history.get(sequence_id)
        if history_resp.status == 404:
            return None
        email = SMTPSerialiser(**json.loads(history.decode('ascii')))
        return email

    def reset(self):
        super(SMTPMock, self).reset()
