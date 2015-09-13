import base64
import json
import re
from pretenders.common.exceptions import NoRequestFound


def to_dict(wsgi_headers, include=lambda _: True):
    """
    Convert WSGIHeaders to a dict so that it can be JSON-encoded
    """
    ret = {}
    for k, v in wsgi_headers.items():
        if include(k):
            ret[k] = v
    return ret


class RequestSerialiser(object):
    """
    Utility class to proxy request from mock to boss.

    It is used to serialise requests as JSON data.
    """
    def __init__(self, path, request):
        if request.query_string:
            path = "{0}?{1}".format(path, request.query_string)

        self.body = binary_to_ascii(request.body.read())
        self.headers = to_dict(request.headers)
        self.method = request.method
        self.url = path
        self.rule = "{0} {1}".format(request.method, path)

    def serialize(self):
        data = {
            'body': self.body,
            'headers': self.headers,
            'method': self.method,
            'url': self.url,
            'rule': self.rule,
        }
        return json.dumps(data)


def binary_to_ascii(data):
    return base64.b64encode(data).decode('ascii')


def ascii_to_binary(data):
    return base64.b64decode(data.encode('ascii'))


class JsonHelper(object):
    """
    Encapsulation of JSON data that can be reused for HTTP traffic.

    It can be initialised from JSON data or from detailed fields,
    that will end up as key/values in a dictionary.

    The JSON-ified data has some specific keys that are treated
    in a special way, as they represent parts of the HTTP requests
    and responses: ``headers``, ``body``, ``status``.

    ``body`` gets a special treatment, as it may contain binary
    data. It is converted to and from Base64 to make it serialisable
    in JSON.

    :param json_data:
        An optional string representing JSON data. It may include the
        following keys, for an HTTP preset:
    :param kwargs:
        Additional keyword arguments will complement or override the
        values in ``json_data``. Normally you will use one or the other.
    """
    def __init__(self, json_data=None, data=None, **kwargs):
        self.data = {}
        if json_data is not None:
            content = json_data.decode('ascii')
            self.data = json.loads(content)
        if data is not None:
            self.data.update(data)
        self.data.update(kwargs)

    def __getattr__(self, attribute):
        """Access attributes from JSON-dict as if they were class attibutes"""
        return self.data[attribute]

    @classmethod
    def from_http_request(cls, pretend_response):
        response, data = pretend_response
        if response.status != 200:
            raise NoRequestFound('No saved request')
        return JsonHelper(data)

    @property
    def body(self):
        """The body field, as binary data"""
        return ascii_to_binary(self.data['body'])

    def as_dict(self):
        """The contained data, as a dictionary"""
        return self.data

    def as_http_response(self, response):
        """
        Generate an HTTP response from the data.

        ``body``, ``headers``, and ``status`` keys are used as such in
        the HTTP response.

        :param response:
            The ``bottle`` object that represents the response.
        """
        for header, value in self.headers.items():
            response.set_header(str(header), str(value))
        response.status = self.status
        return self.body

    def as_json(self):
        """The contained data, as a JSON-serialised string."""
        if isinstance(self.data['rule'], MatchRule):
            self.data['rule'] = self.data['rule'].as_dict()
        return json.dumps(self.data)

    def __str__(self):
        return str(self.data)


class Preset(JsonHelper):
    """A preset instance represents a pre-programmed response."""
    pass


def match_rule_from_dict(data):
    if isinstance(data, dict):
        return MatchRule(
            data['rule'],
            data.get('headers', None),
            data.get('body', None),
        )

    else:
        return MatchRule(data)


class MatchRule(object):
    """
    A matching rule against which incoming requests will be compared.
    """

    def __init__(self, rule, headers=None, body=None):
        """
        :param rule: String incorporating the method and url to be matched
            eg "GET url/to/match"
        :param headers: Dictionary of headers to match.
        :param headers: Body to match (string using regex syntax).
        """
        self.rule = rule
        if headers:
            self.headers = headers
        else:
            self.headers = {}
        self.body = body

    def as_dict(self):
        """ Convert a match rule instance to a dictionary """
        return {
            'rule': self.rule,
            'headers': self.headers,
            'body': self.body,
        }

    def __key(self):
        """ A unique key for a match rule which will be hashable. """
        keys = [self.rule]
        for k, v in self.headers.items():
            keys.append('{0}:{1}'.format(k, v))
        return tuple(keys)

    def __hash__(self):
        return hash(self.__key())

    def matches(self, request):
        """
        Check if a provided request matches this match rule.
        :param request:  A dictionary representing a mock request against which
            we'll attempt to match.
        :return: True if the request is a match for rule and False if not.
        """
        return (self.rule_matches(request['rule'])
                and ('headers' not in request
                     or self.headers_match(request['headers']))
                and ('body' not in request
                     or self.body_match(request['body'])))

    def rule_matches(self, rule):
        """
        Check if a provided request matches the regex in the rule attribute
        :param rule:  The regex rule included in the request we're matching
            against.
        :return: True if the request is a match for rule and False if not.
        """
        try:
            return re.match(self.rule, rule) is not None
        except KeyError:
            return False

    def headers_match(self, headers):
        """
        Check if a provided request matches the dictionary in the
            header attribute
        :param headers:  The dictionary of headers included in the request
            we're matching against.
        :return: True if the request is a match for headers and False if not.
        """
        if self.headers:
            for k, v in self.headers.items():
                try:
                    header = headers[k]
                except KeyError:
                    return False
                else:
                    if header != v:
                        return False
        return True

    def body_match(self, body):
        """
        Check if a provided request matches the regex in the body attribute
        :param body:  A string in regex syntax that will be matched against the
            request body.
        :return: True if the request body matches and False if not.
        """
        if self.body:
            body = ascii_to_binary(body).decode()
            return re.match(self.body, body) is not None
        return True
