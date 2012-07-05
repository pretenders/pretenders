from nose.tools import assert_true, assert_false, assert_equal
import time

try:
    from http.client import HTTPConnection
except ImportError:
    # Python2.6/2.7
    from httplib import HTTPConnection

from pretenders.http.client import HTTPMock, APIHelper
from pretenders.constants import TIMEOUT_MOCK_SERVER
from pretenders.boss.maintain import STALE_DELETE_FREQUENCY


def test_clear_down_of_stale_mock_servers_taking_place():
    #Test that stale mock servers are cleared out
    # TODO: Once the timeout specification can be dictated by the client
    # the sleep in this test can be reduced.
    http_mock = HTTPMock('localhost', 8000)
    mock_servers = http_mock.get_mock_servers()

    assert_true(len(mock_servers) > 0)
    assert_true('{0}'.format(http_mock.mock_access_point_id) in mock_servers)

    # Sleep for enough time for the maintainer to have run and killed the
    # process. which means the total of STALE_DELETE_FREQUENCY + timeout
    #
    timeout = mock_servers[http_mock.mock_access_point_id]['timeout_secs']
    time.sleep(STALE_DELETE_FREQUENCY + timeout)

    post_delete_set = http_mock.get_mock_servers()
    assert_false(http_mock.mock_access_point_id in post_delete_set)


def test_clear_down_only_happens_if_no_request_for_timeout_period():
    # Test that stale mock servers are not cleared if they
    # recently made a request.
    # TODO: Once the timeout specification can be dictated by the client
    # the sleep in this test can be reduced.
    http_mock = HTTPMock('localhost', 8000)
    mock_servers = http_mock.get_mock_servers()
    print(mock_servers)
    print (http_mock.mock_access_point_id)
    mock_server = mock_servers[http_mock.mock_access_point_id]
    timeout_server = mock_server['timeout_secs']
    assert_equal(mock_server['last_call'], mock_server['start'])

    for i in xrange(3):
        # Sleep for a while, check that the server is still running and then
        # make a call to the mock server.

        time.sleep(timeout_server / 2)

        # Check that we are still running
        mock_server = (
            http_mock.get_mock_servers()[http_mock.mock_access_point_id])
        assert_true(mock_server['last_call'] > mock_server['start'])

        # Make a call to the mock server.
        mock_server_client = APIHelper(
                        HTTPConnection(http_mock.mock_access_point),
                        http_mock.mock_access_url
                      )
        mock_server_client.http(
            "GET",
            "{0}/some_url".format(http_mock.mock_access_url)
        )
