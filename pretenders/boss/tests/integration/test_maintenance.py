from nose.tools import assert_true, assert_false, assert_equal, assert_raises
import time

try:
    from http.client import HTTPConnection
except ImportError:
    # Python2.6/2.7
    from httplib import HTTPConnection

from pretenders.http.client import HTTPMock
from pretenders.base import APIHelper
from pretenders.boss.maintain import STALE_DELETE_FREQUENCY
from pretenders.base import ResourceNotFound


def test_clear_down_of_stale_mock_servers_taking_place():
    #Test that stale mock servers are cleared out
    # TODO: Once the timeout specification can be dictated by the client
    # the sleep in this test can be reduced.
    http_mock = HTTPMock('localhost', 8000, pretender_timeout=5)
    pretender = http_mock.get_pretender()

    assert_equal(http_mock.pretend_access_point_id, pretender.uid)

    # Sleep for enough time for the maintainer to have run and killed the
    # process. which means the total of STALE_DELETE_FREQUENCY + timeout
    #
    time.sleep(STALE_DELETE_FREQUENCY + pretender.timeout_in_secs)

    assert_raises(ResourceNotFound, http_mock.get_pretender)


def test_clear_down_only_happens_if_no_request_for_timeout_period():
    # Test that stale mock servers are not cleared if they
    # recently made a request.
    # TODO: Once the timeout specification can be dictated by the client
    # the sleep in this test can be reduced.
    http_mock = HTTPMock('localhost', 8000, pretender_timeout=5)
    pretender = http_mock.get_pretender()

    timeout_server = pretender.timeout_in_secs
    assert_equal(pretender.last_call, pretender.start)

    for i in range(3):
        # Sleep for a while, check that the server is still running and then
        # make a call to the mock server.

        time.sleep(timeout_server / 2)

        # Check that we are still running
        pretender = http_mock.get_pretender()

        # Make a call to the mock server.
        pretender_client = APIHelper(
                        HTTPConnection(http_mock.pretend_access_point),
                        '')
        pretender_client.http(
            method="GET",
            url="/some_url"
        )
