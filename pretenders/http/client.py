from copy import copy
import json

from pretenders.base import APIHelper
from pretenders.boss.client import BossClient
from pretenders.http import HttpRequest, binary_to_ascii


class PresetClient(APIHelper):

    def add(self, match_url='', match_method='', response_status=200,
                response_body=b'', response_headers={}):

        new_preset = {
            'headers': response_headers,
            'body': binary_to_ascii(response_body),
            'status': response_status,
            'rules': [match_url, match_method],
        }
        body = json.dumps(new_preset)

        return self.http('POST', url=self.path, body=body)


class HTTPMock(BossClient):

    def __init__(self, host, boss_port):
        super(HTTPMock, self).__init__(host, boss_port)
        self.preset = PresetClient(self.connection, '/preset')
        self.history = APIHelper(self.connection, '/history')
        self.url = ''
        self.method = ''

    def reset(self):
        self.preset.reset()
        self.history.reset()
        return self

    def when(self, url='', method=''):
        mock = copy(self)
        mock.url = url
        mock.method = method
        return mock

    def reply(self, body=b'', status=200, headers={}):
        self.preset.add(self.url, self.method, status, body, headers)
        return self

    def get_request(self, sequence_id=None):
        return HttpRequest(self.history.get(sequence_id))
