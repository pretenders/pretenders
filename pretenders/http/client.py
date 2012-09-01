from copy import copy

from pretenders.boss.client import BossClient
from pretenders.http import MockHttpRequest
from pretenders.settings import TIMEOUT_PRETENDER


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

    boss_mock_type = 'http'

    def __init__(self, host, port, pretender_timeout=TIMEOUT_PRETENDER):
        """
        Create an HTTPMock client for testing purposes.

        :param host:
            The host of the boss server.

        :param port:
            The port to connect to of the boss.

        :param pretender_timeout:
            The timeout (in seconds) to be passed to the boss when
            instantiating the mock HTTP server. If a request is not received by
            the mock server in this time, it will be closed down by the boss.
        """
        super(HTTPMock, self).__init__(host, port, pretender_timeout)
        self.rule = ''

    def when(self, rule=''):
        """
        Set the match rule which is the first part of the Preset.
        """
        mock = copy(self)
        mock.rule = rule
        return mock

    def reply(self, body=b'', status=200, headers={}, times=1):
        """
        Set the pre-canned reply for the preset.
        """
        self.preset.add(self.rule, status, body, headers, times)
        return self

    def get_request(self, sequence_id=None):
        """
        Get a stored request issued to the mock server, by sequence order.
        """
        return MockHttpRequest(self.history.get(sequence_id))
