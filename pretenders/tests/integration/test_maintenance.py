from nose.tools import assert_equal, assert_raises
import time

from pretenders.client.http import HTTPMock
from pretenders.common.constants import FOREVER
from pretenders.common.exceptions import ResourceNotFound
from pretenders.server.maintain import STALE_DELETE_FREQUENCY
from . import get_fake_client


def test_clear_down_of_stale_mock_servers_taking_place():
    #Test that stale mock servers are cleared out
    # TODO: Once the timeout specification can be dictated by the client
    # the sleep in this test can be reduced.
    http_mock = HTTPMock('localhost', 8000, timeout=5)
    pretender = http_mock.get_pretender()

    assert_equal(http_mock.pretend_access_point_id, pretender.name)

    # Sleep for enough time for the maintainer to have run and killed the
    # process. which means the total of STALE_DELETE_FREQUENCY + timeout
    #
    time.sleep(STALE_DELETE_FREQUENCY + pretender.timeout.seconds)

    assert_raises(ResourceNotFound, http_mock.get_pretender)


def test_clear_down_only_happens_if_no_request_for_timeout_period():
    # Test that stale mock servers are not cleared if they
    # recently made a request.
    # TODO: Once the timeout specification can be dictated by the client
    # the sleep in this test can be reduced.
    http_mock = HTTPMock('localhost', 8000, timeout=5)
    pretender = http_mock.get_pretender()

    timeout_server = pretender.timeout.seconds
    assert_equal(pretender.last_call, pretender.start)

    for i in range(3):
        # Sleep for a while, check that the server is still running and then
        # make a call to the mock server.
        time.sleep(timeout_server / 2)

        # Check that we are still running
        pretender = http_mock.get_pretender()

        # Make a call to the mock server.
        pretender_client = get_fake_client(http_mock)
        pretender_client.get(url="/some_url")


def test_clear_down_removes_history():
    # Test that when we clear down a pretender, the history is removed.
    # Otherwise we end up slowly creeping up the memory usage!
    http_mock = HTTPMock('localhost', 8000, timeout=5)
    pretender = http_mock.get_pretender()
    pretender_client = get_fake_client(http_mock)

    pretender_client.get(url="/some_url")

    assert_equal(http_mock.get_request(0).url, '/some_url')

    time.sleep(STALE_DELETE_FREQUENCY + pretender.timeout.seconds + 1)
    assert_raises(ResourceNotFound, http_mock.get_pretender)
    # Check that there is no history now!
    req = http_mock.get_request(0)
    assert_equal(req, None)


def test_can_create_a_forever_mock():
    # Just test that we can actually create one of these chaps.
    # We won't actually check if it is still around in an eternity.
    mock = HTTPMock('localhost', 8000, timeout=FOREVER)
    assert_equal(FOREVER, mock.get_pretender().timeout)

