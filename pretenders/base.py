import urllib
try:
    from http.client import HTTPConnection
except ImportError:
    # Python2.6/2.7
    from httplib import HTTPConnection


class SubClient(object):

    def __init__(self, base_url, url):
        self.base_url = base_url
        self.url = url
        self.full_url = '{0}{1}'.format(base_url, self.url)
        self.conn = HTTPConnection(base_url)

    def http(self, method, *args, **kwargs):
        # print('Requesting with:', args, kwargs)
        self.conn.request(method=method, *args, **kwargs)
        return self.conn.getresponse()

    def get(self, id):
        return self.http('GET', url='{0}/{1}'.format(self.url, id))

    def list(self, filters={}):
        query_string = ''
        if filters:
            query_string = '?{0}'.format(urllib.urlencode(filters))
        url = '{0}{1}'.format(self.url, query_string)
        return self.http('GET', url=url)

    def reset(self):
        return self.http('DELETE', url=self.url)
