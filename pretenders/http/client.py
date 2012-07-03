import base64
from copy import copy
import json

from pretenders.base import SubClient


class PresetClient(SubClient):

    def add(self, match_url='', match_method='', response_status=200,
                response_body=b'', response_headers={}):

        new_preset = {
            'headers': response_headers,
            'body': base64.b64encode(response_body).decode('ascii'),
            'status': response_status,
            'rules': [match_url, match_method],
        }
        body = json.dumps(new_preset)

        return self.http('POST',
                         url=self.path,
                         body=body)


class HTTPMock(object):

    def __init__(self, host, boss_port):
        self.host = host
        self.boss_port = boss_port
        self.full_host = "{0}:{1}".format(self.host, self.boss_port)

        self.preset = PresetClient(self.full_host, '/preset')
        self.history = SubClient(self.full_host, '/history')
        self.url = ''
        self.method = ''

    def reset(self):
        self.preset.reset()
        self.history.reset()
        return self

    def when(self, url='', method=''):
        mock = copy(self)
        mock.url = url
        mock.method = method
        return mock

    def reply(self, body=b'', status=200, headers={}):
        self.preset.add(self.url, self.method, status, body, headers)
        return self

    def get_request(self, sequence_id=None):
        return Request(self.history.get(sequence_id))


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
