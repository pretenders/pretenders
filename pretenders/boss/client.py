import json
try:
    from http.client import HTTPConnection
except ImportError:
    # Python2.6/2.7
    from httplib import HTTPConnection

from pretenders.base import ResourceNotFound, UnexpectedResponseStatus
from pretenders.base import APIHelper
from pretenders.boss import MockServer
from pretenders.constants import TIMEOUT_MOCK_SERVER


class BossClient(object):

    boss_mock_type = ''

    def __init__(self, host, port, mock_timeout=TIMEOUT_MOCK_SERVER):
        self.host = host
        self.port = port
        self.mock_timeout = mock_timeout
        self.full_host = "{0}:{1}".format(self.host, self.port)

        self.connection = HTTPConnection(self.full_host)
        self.boss_access = APIHelper(self.connection, '')

        (self.mock_access_point,
         self.mock_access_point_id) = self._request_mock_access()

    @property
    def create_mock_url(self):
        return "/mock_server/{0}".format(self.boss_mock_type)

    def _request_mock_access(self):
        """
        Ask the boss to create a mock server by POSTing to ``create_mock_url``

        :returns:
            A tuple containing:

                position 0: url to the mock server
                position 1: unique id of the mock server (for teardown
                            purposes)
        """
        if self.boss_mock_type:
            post_body = json.dumps({'mock_timeout': self.mock_timeout})
            response = self.boss_access.http('POST',
                                             url=self.create_mock_url,
                                             body=post_body)
            mock_server_json = response.read().decode('ascii')
            mock_server_details = json.loads(mock_server_json)
            return mock_server_details["url"], mock_server_details["id"]
        return "", ""

    @property
    def delete_mock_url(self):
        return "{0}/{1}".format(self.create_mock_url,
                                self.mock_access_point_id)

    def get_mock_server(self):
        "Get mock servers from the server in dict format"
        response = self.boss_access.http(
            method='GET',
            url='/mock_server/{0}'.format(self.mock_access_point_id),
        )
        if response.status == 200:
            return MockServer.from_json_response(response)
        elif response.status == 404:
            raise ResourceNotFound(
                    'The mock server for this client was shutdown.')
        else:
            raise UnexpectedResponseStatus(response.status)
