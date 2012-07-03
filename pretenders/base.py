import urllib


class APIHelper(object):

    def __init__(self, connection, path):
        self.connection = connection
        self.path = path

    def http(self, method, *args, **kwargs):
        self.connection.request(method=method, *args, **kwargs)
        return self.connection.getresponse()

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
