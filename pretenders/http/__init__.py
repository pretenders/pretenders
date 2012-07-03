import base64
import json


def to_dict(wsgi_headers, include=lambda _: True):
    """
    Convert WSGIHeaders to a dict so that it can be JSON-encoded
    """
    ret = {}
    for k, v in wsgi_headers.items():
        if include(k):
            ret[k] = v
    return ret


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


def binary_to_ascii(data):
    return base64.b64encode(data).decode('ascii')


def ascii_to_binary(data):
    return base64.b64decode(data.encode('ascii'))


class RequestInfo(object):
    def __init__(self, path, request):
        if request.query_string:
            path = "{0}?{1}".format(path, request.query_string)

        self.body = base64.b64encode(request.body.read()).decode('ascii')
        self.headers = to_dict(request.headers)
        self.method = request.method
        self.url = path
        self.match = [path, request.method]

    def serialize(self):
        data = {
            'body': self.body,
            'headers': self.headers,
            'method': self.method,
            'url': self.url,
            'match': [self.url, self.method],
        }
        return json.dumps(data)


class Preset(object):
    def __init__(self, data):
        content = data.decode('ascii')
        self.preset = json.loads(content)
        self.rule = tuple(self.preset['rules'])

    def as_dict(self):
        return self.preset

    def as_http_response(self, response):
        for header, value in self.preset['headers'].items():
            response.set_header(header, value)
        response.status = self.preset['status']
        return ascii_to_binary(self.preset['body'])

    def as_json(self):
        return json.dumps(self.preset)


class HttpRequest(object):
    """A stored HTTP request as issued to our pretend server"""
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
