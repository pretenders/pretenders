try:
    from http.client import HTTPConnection
except ImportError:
    # Python2.6/2.7
    from httplib import HTTPConnection

from pretenders.http.client import APIHelper


class FakeClient(APIHelper):

    def get(self, url, *args, **kwargs):
        url = "{0}{1}".format(self.path, url)
        return self.http('GET', url=url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        url = "{0}{1}".format(self.path, url)
        return self.http('POST', url=url, *args, **kwargs)


def get_fake_client(boss_client):
    return FakeClient(HTTPConnection(boss_client.mock_access_point), '')
