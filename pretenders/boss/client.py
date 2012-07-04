import json
try:
    from http.client import HTTPConnection
except ImportError:
    # Python2.6/2.7
    from httplib import HTTPConnection

from pretenders.base import APIHelper


class BossClient(object):

    create_mock_url = ''

    def __init__(self, host, boss_port):
        self.host = host
        self.boss_port = boss_port
        self.full_host = "{0}:{1}".format(self.host, self.boss_port)

        self.connection = HTTPConnection(self.full_host)
        self.boss_accesss = APIHelper(self.connection, '')

        (self.mock_access_point,
         self.mock_access_point_id) = self._request_mock_access()

    def _request_mock_access(self):
        """
        Ask the boss to create a mock server by POSTing to ``create_mock_url``

        :returns:
            A tuple containing:

                position 0: url to the mock server
                position 1: unique id of the mock server (for teardown
                            purposes)
        """
        if self.create_mock_url:
            response = self.boss_accesss.http('POST', url=self.create_mock_url)
            mock_server_json = response.read().decode('ascii')
            mock_server_details = json.loads(mock_server_json)
            return mock_server_details["url"], mock_server_details["id"]
        return "", ""
