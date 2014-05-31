import requests
from nose.tools import assert_equals

from pretenders.client.http import HTTPMock
from . import get_fake_client


def test_get_mock_server_by_name():
    http_mock = HTTPMock('localhost', 8000, timeout=5, name='fred')
    # Check that we are using the name path
    assert_equals(http_mock.pretend_access_point, "localhost:8000")
    assert_equals(http_mock.pretend_access_path, "/mockhttp/fred")

    # Set up a rule
    http_mock.when('POST /someplace').reply(b"something interesting", 200)

    # Perform a post from a pretend application
    fake_client = get_fake_client(http_mock)
    response, data = fake_client.post(url='/someplace', body="anything".encode())

    # check the app would receive back the response from the rule we set up.
    assert_equals(response.status, 200)
    assert_equals(data, b'something interesting')

    # finally, check that we can look at the history via the http_mock.
    req = http_mock.get_request(0)
    assert_equals(req.method, 'POST')
    assert_equals(req.url, '/someplace')

    http_mock.delete_mock()


def test_creating_second_mock_server_by_same_name_gives_original_server():
    # Create 1
    h1 = HTTPMock('localhost', 8000, timeout=5, name='duplicate_test')
    # Create another
    h2 = HTTPMock('localhost', 8000, timeout=5, name='duplicate_test_2')
    # Creation of one with a duplicate name should succeed.
    h3 = HTTPMock('localhost', 8000, name='duplicate_test')

    # Requests to h1 should be visible by h3. h2 should only be seen by it.

    get_fake_client(h1).get(url='/h1_get')
    get_fake_client(h2).get(url='/h2_get')
    get_fake_client(h3).get(url='/h3_get')

    # assert that the requests h1 and h3 requests can be seen via both mocks.
    assert_equals(h1.get_request(0).url, h3.get_request(0).url)
    assert_equals(h1.get_request(1).url, h3.get_request(1).url)
    assert_equals(h2.get_request(0).url, '/h2_get')

    h1.delete_mock()
    h2.delete_mock()


def test_pretend_url():
    "Test that pretend url works"
    h1 = HTTPMock('localhost', 8000, timeout=5, name='some_mock')
    assert_equals(h1.pretend_url, 'http://localhost:8000/mockhttp/some_mock')


def test_get_response_when_none_queued():
    h1 = HTTPMock('localhost', 8000, timeout=5, name='existent')

    THIRD_PARTY_ADDRESS = 'http://localhost:8000/mockhttp/existent'
    resp = requests.get(THIRD_PARTY_ADDRESS + '/hello')
    assert_equals(resp.status_code, 404)


def test_get_response_from_non_existent_mock_server():
    THIRD_PARTY_ADDRESS = 'http://localhost:8000/mockhttp/non-existent'

    resp = requests.get(THIRD_PARTY_ADDRESS + '/hello')

    assert_equals(resp.status_code, 404)
