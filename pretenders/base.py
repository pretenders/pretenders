import urllib
try:
    from http.client import HTTPConnection
except ImportError:
    # Python2.6/2.7
    from httplib import HTTPConnection


class SubClient(object):

    def __init__(self, conn=None, root_url=None, path=''):
        self.root_url = root_url
        self.path = path
        self.full_url = '{0}{1}'.format(root_url, self.path)
        self._conn = None

    def http(self, method, *args, **kwargs):
        self.conn.request(method=method, *args, **kwargs)
        return self.conn.getresponse()

    def get(self, id):
        return self.http('GET', url='{0}/{1}'.format(self.path, id))

    def list(self, filters={}):
        query_string = ''
        if filters:
            query_string = '?{0}'.format(urllib.urlencode(filters))
        url = '{0}{1}'.format(self.path, query_string)
        return self.http('GET', url=url)

    def reset(self):
        return self.http('DELETE', url=self.path)

    @property
    def conn(self):
        if not self._conn:
            self._conn = HTTPConnection(self.root_url)
        return self._conn
