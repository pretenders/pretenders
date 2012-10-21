import json
try:
    from http.client import HTTPConnection
except ImportError:
    # Python2.6/2.7
    from httplib import HTTPConnection

from pretenders.base import (
    get_logger, ResourceNotFound, UnexpectedResponseStatus
)
from pretenders.base import APIHelper
from pretenders.boss import PretenderModel
from pretenders.exceptions import ConfigurationError
from pretenders.http import binary_to_ascii, Preset


LOGGER = get_logger('pretenders.boss.client')


class PresetHelper(APIHelper):

    def add(self, match_rule=None, response_status=200,
            response_body=b'', response_headers={}, times=1):
        """
        Add a new preset to the boss server.
        """
        new_preset = Preset(
            headers=response_headers,
            body=binary_to_ascii(response_body),
            status=response_status,
            rule=match_rule,
            times=times,
        )

        response = self.http('POST', url=self.path, body=new_preset.as_json())
        if response.status != 200:
            raise ConfigurationError(response.read().decode())
        return response


class BossClient(object):

    boss_mock_type = None

    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.full_host = "{0}:{1}".format(self.host, self.port)

        self.connection = HTTPConnection(self.full_host)
        self.boss_access = APIHelper(self.connection, '')

        LOGGER.info('Requesting {0} pretender. Port:{1} Timeout:{2}'
                    .format(self.boss_mock_type, self.port, self.timeout))
        if self.boss_mock_type:
            self.pretender_details = self._request_mock_access()
        else:
            self.pretender_details = {}

        self.history = APIHelper(self.connection,
                                 '/history/{0}'.format(
                                            self.pretend_access_point_id))
        self.preset = PresetHelper(self.connection,
                                   '/preset/{0}'.format(
                                            self.pretend_access_point_id))

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
        if self.timeout:
            post_body = json.dumps({'pretender_timeout': self.timeout})
        else:
            post_body = '{}'
        response = self.boss_access.http('POST',
                                         url=self.create_mock_url,
                                         body=post_body)
        pretender_json = response.read().decode('ascii')
        pretender_details = json.loads(pretender_json)

        return pretender_details

    @property
    def delete_mock_url(self):
        return "{0}/{1}".format(self.create_mock_url,
                                self.pretend_access_point_id)

    def get_pretender(self):
        "Get pretenders from the server in dict format"
        response = self.boss_access.http(
            method='GET',
            url='/{0}/{1}'.format(self.boss_mock_type,
                                  self.pretend_access_point_id),
        )
        if response.status == 200:
            return PretenderModel.from_json_response(response)
        elif response.status == 404:
            raise ResourceNotFound(
                    'The mock server for this client was shutdown.')
        else:
            raise UnexpectedResponseStatus(response.status)
