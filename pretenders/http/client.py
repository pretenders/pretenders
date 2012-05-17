import urllib
import http.client


class SubClient(object):

    def __init__(self, base_url, url):
        self.base_url = base_url
        self.url = url
        self.full_url = '{0}{1}'.format(base_url, self.url)
        self.conn = http.client.HTTPConnection(base_url)

    def request(self, *args, **kwargs):
        print(args, kwargs)
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
        print(url)
        return self.do_get(url=url)

    def reset(self):
        return self.do_delete(url=self.url)

    def get_by_id(self, unique_id):
        return self.do_get(url='{0}/{1}'.format(self.url, unique_id))


class PresetClient(SubClient):

    def add(self, match_path='', match_method='', response_status=200,
                response_body='', response_headers={}):
        headers = response_headers.copy()
        headers.update({
            'X-Pretend-Match-Path': match_path,
            'X-Pretend-Match-Method': match_method,
            'X-Pretend-Response-Status': response_status,
        })
        return self.do_post(url=self.url,
                            body=response_body,
                            headers=headers)


class MockClient(SubClient):

    def get(self, url, *args, **kwargs):
        url = "{0}{1}".format(self.url, url)
        return self.do_get(url=url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        url = "{0}{1}".format(self.url, url)
        return self.do_post(url=url, *args, **kwargs)


class Client(object):

    def __init__(self, host, port=9000):
        self.host = host
        self.port = port
        full_host = "{0}:{1}".format(self.host, self.port)

        self.preset = PresetClient(full_host, '/preset')
        self.history = SubClient(full_host, '/history')
        self._mock = MockClient(full_host, '/mock')

    def reset_all(self):
        self.preset.reset()
        self.history.reset()

    def add_preset(self, *args, **kwargs):
        return self.preset.add(*args, **kwargs)

    def get_request(self, sequence_id=None):
        return Request(self.history.get_by_id(sequence_id))


class Request(object):
    """A stored request as issued to our pretend server"""
    def __init__(self, pretend_response):
        if pretend_response.status != 200:
            # TODO use custom exception
            raise Exception('No saved request')
        self.response = pretend_response
        self.headers = dict(self.response.getheaders())
        self.method = self.headers['X-Pretend-Request-Method']
        del self.headers['X-Pretend-Request-Method']
        self.path = self.headers['X-Pretend-Request-Path']
        del self.headers['X-Pretend-Request-Path']
        self._request_body = None
        del self.headers['Server']

    @property
    def body(self):
        if not self._request_body:
            self._request_body = self.response.read()
        return self._request_body


if __name__ == '__main__':
    c = Client('localhost', 8000)
    c.add_preset(match_path='/fred/test/one',
                 match_method='GET',
                 response_status=200,
                 response_body='You tested fred well')

    response = c._mock.get(url='/fred/test/one')
    response = c.get_request(0)
    print(response.getheaders())
    print(response.read())
