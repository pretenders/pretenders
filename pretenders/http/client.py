from copy import copy

from pretenders.base import APIHelper
from pretenders.boss.client import BossClient
from pretenders.http import binary_to_ascii, HttpRequest, Preset


class PresetClient(APIHelper):

    def add(self, match_rule='', response_status=200,
                response_body=b'', response_headers={}):
        """
        Add a new preset to the boss server.
        """
        new_preset = Preset(
            headers=response_headers,
            body=binary_to_ascii(response_body),
            status=response_status,
            rule=match_rule
        )
        return self.http('POST', url=self.path, body=new_preset.as_json())


class HTTPMock(BossClient):
    """
    A mock HTTP server as seen from the test writer.

    The test will first preset responses on the server, and after execution
    it will enquire the received requests.

    Example usage::

        from pretenders.http.client import HTTPMock
        mock = HTTPMock('localhost', 8000)
        mock.when('/hello', 'GET').reply('Hello')
        # run tests... then read received responses:
        r = mock.get_request(0)
        assert_equal(r.method, 'GET')
        assert_equal(r.url, '/hello?city=barcelona')
    """

    create_mock_url = '/mock_server/http'

    def __init__(self, host, boss_port):
        super(HTTPMock, self).__init__(host, boss_port)
        self.preset = PresetClient(self.connection, '/preset')
        self.history = APIHelper(self.connection, '/history')
        self.rule = ''

    def reset(self):
        """
        Delete all presets and history.
        """
        self.preset.reset()
        self.history.reset()
        return self

    def when(self, rule=''):
        """
        Set the match rule which is the first part of the Preset.
        """
        mock = copy(self)
        mock.rule = rule
        return mock

    def reply(self, body=b'', status=200, headers={}):
        """
        Set the pre-canned reply for the preset.
        """
        self.preset.add(self.rule, status, body, headers)
        return self

    def get_request(self, sequence_id=None):
        """
        Get a stored request issued to the mock server, by sequence order.
        """
        return HttpRequest(self.history.get(sequence_id))
