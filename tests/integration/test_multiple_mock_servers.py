from nose.tools import assert_equals

from pretenders.client.http import HTTPMock
from . import get_fake_client


http_mock = HTTPMock('localhost', 8000)


def assert_response_equal(http_response, body, status):
    response, data = http_response
    assert_equals(response.status, status)
    assert_equals(data, body)


def test_multiple_mock_servers_only_see_their_presets_and_history():
    first_mock = HTTPMock('localhost', 8000, timeout=30)
    second_mock = HTTPMock('localhost', 8000, timeout=30)

    first_mock_response_body = b"a 1st mock fake response"
    second_mock_response_body = b"a 2nd mock fake response"
    # Set up the two mocks to respond differently:
    # Set up first mock to respond with a 200 twice.
    for i in range(2):
        first_mock.when('POST /someplace').reply(first_mock_response_body,
                                                 200)
        second_mock.when('POST /someplace').reply(second_mock_response_body,
                                                  601)

    # create some fake clients that will post to the mock servers.
    first_fake_client = get_fake_client(first_mock)
    second_fake_client = get_fake_client(second_mock)

    # Make some requests using the clients
    # We alternate between the client calls, asserting that the responses match
    # those set up above.
    for i in range(2):
        post_body = "first_mock_{0}".format(i).encode()
        response = first_fake_client.post(url='/someplace',
                                          body=post_body)
        assert_response_equal(response, first_mock_response_body, 200)

        # Check that the historical values match those requested.
        request = first_mock.get_request(i)
        assert_equals(request.method, 'POST')
        assert_equals(request.url, '/someplace')
        assert_equals(request.body, post_body)

    for i in range(2):
        post_body = "second_mock_{0}".format(i).encode()

        response = second_fake_client.post(url='/someplace',
                                           body=post_body)
        assert_response_equal(response, second_mock_response_body, 601)

        # Check that the historical values match those requested.
        request = second_mock.get_request(i)
        assert_equals(request.method, 'POST')
        assert_equals(request.url, '/someplace')
        assert_equals(request.body, post_body)
