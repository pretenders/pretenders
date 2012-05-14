import json
import urllib
import http.client


class Preset(object):

    def __init__(self,
                 match_url,
                 match_method,
                 response_status,
                 response_body,
                 response_encoding='utf-8'):
        self.match_url = match_url
        self.match_method = match_method
        self.response_status = response_status
        self.response_body = response_body
        self.response_encoding = response_encoding

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
           }
        })


class SubClient(object):
    def __init__(self, base_url, url):
        self.base_url = base_url
        self.url = url
        self.full_url = '{0}{1}'.format(base_url, self.url)

        self.conn = http.client.HTTPConnection(base_url)

    def list(self, filters={}):
        query_string = ''
        if filters:
            query_string = '?{0}'.format(urllib.urlencode(filters))

        self.conn.request(url='{0}{1}'.format(self.full_url, query_string),
                          method="GET")
        return self.conn.getresponse()

    def reset(self):
        self.conn.request(url=self.full_url, method="DELETE")
        return self.conn.getresponse()

    def get(self, unique_id):
        self.conn.request(url='{0}/{1}'.format(self.full_url, unique_id),
                          method="GET")
        return self.conn.getresponse()


class PresetClient(SubClient):

    def add(self, *args, **kwargs):
        p = Preset(*args, **kwargs)
        self.conn.request(url=self.full_url,
                          method="POST",
                          body=p.serialize())
        return self.conn.getresponse()


class Client(object):

    def __init__(self, host, configuration_port=9001):
        self.host = host
        self.configuration_port = configuration_port
        self.full_config_host = "{0}:{1}".format(self.host,
                                                 self.configuration_port)
        self.preset = PresetClient(self.full_config_host, '/preset')
        self.history = SubClient(self.full_config_host, '/history')


if __name__ == '__main__':
    c = Client('localhost', 8000)
    c.preset.add(match_url='/fred/test/one',
                 match_method='POST',
                 response_status=200,
                 response_body='You tested fred well')
    c.preset.reset()
    print(c.history.list().read())
