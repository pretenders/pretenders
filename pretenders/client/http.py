from copy import copy
import json

from pretenders.client import BossClient
from pretenders.common.http import MatchRule, JsonHelper
from pretenders.common.exceptions import NoRequestFound


class HTTPMock(BossClient):
    """
    A mock HTTP server as seen from the test writer.

    The test will first preset responses on the server, and after execution
    it will enquire the received requests.

    Example usage::

        from pretenders.client.http import HTTPMock
        mock = HTTPMock('localhost', 8000)
        mock.when('GET /hello').reply('Hello')
        # run tests... then read received responses:
        r = mock.get_request(0)
        assert_equal(r.method, 'GET')
        assert_equal(r.url, '/hello?city=barcelona')
    """

    boss_mock_type = 'http'

    def __init__(self, host, port, timeout=None, name=None):
        """
        Create an HTTPMock client for testing purposes.

        :param host:
            The host of the boss server.

        :param port:
            The port to connect to of the boss.

        :param timeout:
            The timeout (in seconds) to be passed to the boss when
            instantiating the mock HTTP server. If a request is not received by
            the mock server in this time, it will be closed down by the boss.

        :param name:
            The name of the mock. If an HTTP Mock server exists with this name
            the client will be hooked into use that server. Otherwise a new one
            will be created for the client.
        """
        super(HTTPMock, self).__init__(host, port, timeout, name)
        self.rule = ''

    @property
    def pretend_access_path(self):
        return self.pretender_details['path']

    @property
    def pretend_url(self):
        """
        The full URL of the pretend server.
        """
        if self.port == 80:
            full_host = self.host
        else:
            full_host = "{0}:{1}".format(self.host, self.port)
        return "http://{0}{1}".format(
            full_host, self.pretend_access_path
        )

    def when(self, rule='', headers=None, body=None):
        """
        Set the match rule which is the first part of the Preset.

        :param rule: String incorporating the method and url to match
            eg "GET url/to/match"
        :param headers: An optional dictionary of headers to match.

        .. note::

            ``rule`` is matched as a regular expression and can therefore be
            set to match more than one request.
            eg. ``r'^GET /something/([a-zA-Z0-9\-_]*)/?'``

            Also note that it is always seen as a regex and therefore to match
            ``"GET /foo?bar=1"`` you would need to use something like::

            'GET /foo\?bar=1'

        """
        match_rule = MatchRule(rule, headers, body)
        mock = copy(self)
        mock.rule = match_rule
        return mock

    def reply(self, body=b'', status=200, headers={}, times=1, after=0):
        """
        Set the pre-canned reply for the preset.

        :param after:
            The http mock server will delay for ``after`` seconds before
            replying. Defaults to 0.

        """
        self.preset.add(self.rule, status, body, headers, times, after)
        return self

    def get_request(self, sequence_id=None):
        """
        Get a stored request issued to the mock server, by sequence order.

        If sequence_id is not given return the whole history of requests to
        this mock.
        """
        try:
            if sequence_id is not None:
                historical = self.history.get(sequence_id)
                return JsonHelper.from_http_request(historical)
            else:
                response, json_data = self.history.list()
                content = json_data.decode('ascii')
                data = json.loads(content)
                historical = []
                for response in data:
                    historical.append(JsonHelper(data=response))
                return historical
        except NoRequestFound:
            return None
