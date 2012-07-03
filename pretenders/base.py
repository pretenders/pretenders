import urllib


class SubClient(object):

    def __init__(self, get_conn, path):
        print(get_conn, path)
        self.get_conn = get_conn
        self.path = path
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
            print(self.get_conn)
            self._conn = self.get_conn()
        return self._conn
