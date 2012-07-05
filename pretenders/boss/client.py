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
        self.boss_access = APIHelper(self.connection, '')

        (self.mock_access_point,
         self.mock_access_point_id) = self._request_mock_access()

        self.mock_access_url = "/mock/{0}".format(self.mock_access_point_id)

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
            response = self.boss_access.http('POST', url=self.create_mock_url)
            mock_server_json = response.read().decode('ascii')
            mock_server_details = json.loads(mock_server_json)
            return mock_server_details["url"], mock_server_details["id"]
        return "", ""

    @property
    def delete_mock_url(self):
        return "{0}/{1}".format(self.create_mock_url,
                                self.mock_access_point_id)

    def get_mock_servers(self):
        "Get mock servers from the server in dict format"
        results = self.boss_access.http(method='GET', url='/mock_server')
        return json.loads(results)
