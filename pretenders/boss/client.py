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

        self.mock_access_point = self._request_mock_access()

    def _request_mock_access(self):
        if self.create_mock_url:
            response = self.boss_accesss.http('GET', url=self.create_mock_url)
            return response.read()
