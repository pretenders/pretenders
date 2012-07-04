from nose.tools import assert_true, assert_false
import time

from pretenders.http.client import HTTPMock
from pretenders.constants import TIMEOUT_MOCK_SERVER
from pretenders.boss.maintain import STALE_DELETE_FREQUENCY


def test_clear_down_of_stale_mock_servers_taking_place():
    #Test that stale mock servers are cleared out
    # TODO: Once the timeout specification can be dictated by the client
    # the sleep in this test can be reduced.
    http_mock = HTTPMock('localhost', 8000)
    results = http_mock.get_mock_servers()

    print(results)
    assert_true(len(results > 0))
    assert_true(http_mock.mock_access_point_id in results)

    # Sleep for enough time for the maintainer to have run and killed the
    # process. which means the total of STALE_DELETE_FREQUENCY + timeout
    #
    time.sleep(STALE_DELETE_FREQUENCY + TIMEOUT_MOCK_SERVER)

    post_delete_set = http_mock.get_mock_servers()
    assert_false(http_mock.mock_access_point_id in post_delete_set)
    assert_true(False)
