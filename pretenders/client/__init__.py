import json
import logging
try:
    from http import client as httplib
except ImportError:
    # Python 2.6/2.7
    import httplib

import urllib

from pretenders.common.exceptions import (
    ConfigurationError, ResourceNotFound, UnexpectedResponseStatus)
from pretenders.common.pretender import PretenderModel
from pretenders.common.http import binary_to_ascii, Preset


LOGGER = logging.getLogger('pretenders.client')


class APIHelper(object):

    def __init__(self, connection, path):
        self.connection = connection
        self.path = path

    def _get_response(self, method, *args, **kwargs):
        self.connection.request(method=method, *args, **kwargs)
        return self.connection.getresponse()

    def http(self, method, *args, **kwargs):
        """
        Issue an HTTP request.

        The HTTP connection is reused between requests. We try to detect
        dropped connections, and in those cases try to reconnect to the remote
        server.
        """
        try:
            response = self._get_response(method, *args, **kwargs)
        except (httplib.CannotSendRequest, httplib.BadStatusLine):
            self.connection.close()
            self.connection.connect()
            response = self._get_response(method, *args, **kwargs)

        return response, response.read()

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


class PresetHelper(APIHelper):

    def add(self, match_rule=None, response_status=200,
            response_body=b'', response_headers={}, times=1, after=0):
        """
        Add a new preset to the boss server.
        """
        new_preset = Preset(
            headers=response_headers,
            body=binary_to_ascii(response_body),
            status=response_status,
            rule=match_rule,
            times=times,
            after=after
        )

        response, data = self.http('POST', url=self.path,
                                   body=new_preset.as_json())
        if response.status != 200:
            raise ConfigurationError(data.decode())
        return response


class BossClient(object):

    boss_mock_type = None

    def __init__(self, host, port, timeout=None, name=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.name = name
        self.full_host = "{0}:{1}".format(self.host, self.port)

        self.connection = httplib.HTTPConnection(self.full_host)
        self.boss_access = APIHelper(self.connection, '')

        LOGGER.info('Requesting {0} pretender. Port:{1} Timeout:{2} ({3})'
                    .format(self.boss_mock_type, self.port, self.timeout,
                            self.name))
        if self.boss_mock_type:
            self.pretender_details = self._request_mock_access()
        else:
            self.pretender_details = {}

        self.history = APIHelper(
            self.connection,
            '/history/{0}'.format(self.pretend_access_point_id)
        )
        self.preset = PresetHelper(
            self.connection,
            '/preset/{0}'.format(self.pretend_access_point_id)
        )

    def reset(self):
        """
        Delete all history.
        """
        self.history.reset()
        self.preset.reset()
        return self

    @property
    def create_mock_url(self):
        return "/{0}".format(self.boss_mock_type)

    @property
    def pretend_access_point_id(self):
        return self.pretender_details.get('id', "")

    @property
    def pretend_access_point(self):
        return self.full_host

    def _request_mock_access(self):
        """
        Ask the boss to create a mock server by POSTing to ``create_mock_url``

        :returns:
            A tuple containing:

                position 0: hostname[:port] of the mock server
                position 1: unique id of the pretender (for teardown
                            purposes)
        """
        post_body = {'name': self.name}
        if self.timeout:
            post_body['pretender_timeout'] = self.timeout

        post_body = json.dumps(post_body)

        response, data = self.boss_access.http('POST',
                                               url=self.create_mock_url,
                                               body=post_body)
        pretender_json = data.decode('ascii')
        pretender_details = json.loads(pretender_json)
        return pretender_details

    @property
    def delete_mock_url(self):
        return "{0}/{1}".format(self.create_mock_url,
                                self.pretend_access_point_id)

    def delete_mock(self):
        "Delete the mock server that this points to."
        response, data = self.boss_access.http(
            method="DELETE",
            url=self.delete_mock_url)
        if not response.status == 200:
            raise Exception("Delete failed")

    def get_pretender(self):
        "Get pretenders from the server in dict format"
        response, data = self.boss_access.http(
            method='GET',
            url='/{0}/{1}'.format(self.boss_mock_type,
                                  self.pretend_access_point_id),
        )
        if response.status == 200:
            return PretenderModel.from_json_response(data)
        elif response.status == 404:
            raise ResourceNotFound(
                'The mock server for this client was shutdown.')
        else:
            raise UnexpectedResponseStatus(response.status)
