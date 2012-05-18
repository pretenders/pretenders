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

    def request(self, *args, **kwargs):
        print('Requesting with:', args, kwargs)
        self.conn.request(*args, **kwargs)
        return self.conn.getresponse()

    def do_post(self, *args, **kwargs):
        return self.request(method="POST", *args, **kwargs)

    def do_get(self, *args, **kwargs):
        return self.request(method="GET", *args, **kwargs)

    def do_delete(self, *args, **kwargs):
        return self.request(method="DELETE", *args, **kwargs)

    def list(self, filters={}):
        query_string = ''
        if filters:
            query_string = '?{0}'.format(urllib.urlencode(filters))
        url = '{0}{1}'.format(self.url, query_string)

        return self.do_get(url=url)

    def reset(self):
        return self.do_delete(url=self.url)

    def get_by_id(self, unique_id):
        return self.do_get(url='{0}/{1}'.format(self.url, unique_id))


class PresetClient(SubClient):

    def add(self, match_url='', match_method='', response_status=200,
                response_body='', response_headers={}):
        headers = response_headers.copy()
        headers.update({
            'X-Pretend-Match-Url': match_url,
            'X-Pretend-Match-Method': match_method,
            'X-Pretend-Response-Status': response_status,
        })
        return self.do_post(url=self.url,
                            body=response_body,
                            headers=headers)


class Client(object):

    def __init__(self, host, port=9000):
        self.host = host
        self.port = port
        full_host = "{0}:{1}".format(self.host, self.port)

        self.preset = PresetClient(full_host, '/preset')
        self.history = SubClient(full_host, '/history')

    def reset_all(self):
        self.preset.reset()
        self.history.reset()

    def add_preset(self, *args, **kwargs):
        return self.preset.add(*args, **kwargs)

    def get_request(self, sequence_id=None):
        return Request(self.history.get_by_id(sequence_id))


class CaseInsensitiveDict(dict):
    "A dictionary that is case insensitive for keys."

    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveDict, self).__init__(*args, **kwargs)
        for key, value in self.items():
            super(CaseInsensitiveDict, self).__delitem__(key)
            self[key.lower()] = value

    def __delitem__(self, key):
        return super(CaseInsensitiveDict, self).__delitem__(key.lower())

    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(key.lower())


class Request(object):
    """A stored request as issued to our pretend server"""
    def __init__(self, pretend_response):
        if pretend_response.status != 200:
            # TODO use custom exception
            raise Exception('No saved request')
        self.response = pretend_response
        self.headers = CaseInsensitiveDict(self.response.getheaders())
        self.method = self.headers['X-Pretend-Request-Method']
        del self.headers['X-Pretend-Request-Method']
        self.url = self.headers['X-Pretend-Request-Url']
        del self.headers['X-Pretend-Request-Url']
        self._request_body = None
        del self.headers['Server']

    @property
    def body(self):
        if not self._request_body:
            self._request_body = self.response.read()
        return self._request_body
