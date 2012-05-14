import json
import urllib
import http.client


class Preset(object):

    def __init__(self,
                 match_url='',
                 match_method='',
                 response_status=200,
                 response_body='',
                 response_headers={},
                 response_encoding='ascii'):
        self.match_url = match_url
        self.match_method = match_method
        self.response_status = response_status
        self.response_body = response_body
        self.response_encoding = response_encoding
        self.response_headers = response_headers

    def serialize(self):
        return json.dumps({
           'match': {
               'url': self.match_url,
               'method': self.match_method
           },
           'response': {
                'status': self.response_status,
                'body': self.response_body,
                'encoding': self.response_encoding,
                'headers': self.response_headers
           }
        })


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

        return self.do_get(url='{0}{1}'.format(self.full_url, query_string))

    def reset(self):
        return self.do_delete(url=self.full_url)

    def get_by_id(self, unique_id):
        return self.do_get(url='{0}/{1}'.format(self.full_url, unique_id))


class PresetClient(SubClient):

    def add(self, *args, **kwargs):
        p = Preset(*args, **kwargs)
        return self.do_post(url=self.full_url, body=p.serialize())


class MockClient(SubClient):

    def get(self, url, *args, **kwargs):
        url = "{0}{1}".format(self.full_url, url)
        return self.do_get(url=url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        url = "{0}{1}".format(self.full_url, url)
        return self.do_get(url=url, *args, **kwargs)


class Client(object):

    def __init__(self, host, configuration_port=9001, mock_port=9000):
        self.host = host
        self.configuration_port = configuration_port
        self.mock_port = mock_port
        full_config_host = "{0}:{1}".format(self.host, self.configuration_port)
        full_mock_host = "{0}:{1}".format(self.host, self.mock_port)

        self.preset = PresetClient(full_config_host, '/preset')
        self.history = SubClient(full_config_host, '/history')
        self._mock = MockClient(full_mock_host, '/mock')

    def reset_all(self):
        self.preset.reset()
        self.history.reset()

    def add_preset(self, *args, **kwargs):
        return self.preset.add(*args, **kwargs)

    def get_requests(self, sequence_id=None):
        if sequence_id is not None:
            result = self.history.get_by_id(sequence_id)
        else:
            result = self.history.list()
        try:
            return json.loads(str(result.read()))
        except ValueError:
            return []


if __name__ == '__main__':
    c = Client('localhost', 8000)
    c.add_preset(match_url='/fred/test/one',
                 match_method='GET',
                 response_status=200,
                 response_body='You tested fred well')

    print(c.get_requests())

    c.reset_all()
