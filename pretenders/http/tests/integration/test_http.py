from nose.tools import assert_equals, assert_true, assert_raises

from pretenders.constants import PRETEND_PORT_RANGE, FOREVER
from pretenders.exceptions import ConfigurationError
from pretenders.http.client import HTTPMock
from pretenders.http.tests.integration import get_fake_client


http_mock = HTTPMock('localhost', 8000)
fake_client = get_fake_client(http_mock)


def add_test_preset(rule='POST /fred/test/one',
                    body=b'You tested fred well',
                    status=200):
    http_mock.when(rule).reply(body, status)


def test_configure_request_and_check_values():
    "Requires a running pretender.http.server instance"
    http_mock.reset()
    add_test_preset()
    response = fake_client.post(url='/fred/test/one')
    assert_equals(response.status, 200)
    assert_equals(response.read(), b'You tested fred well')

    request = http_mock.get_request(0)

    assert_equals(request.method, 'POST')
    assert_equals(request.url, '/fred/test/one')
    assert_equals(request.body, b'')


def test_perform_wrong_method_on_configured_url():
    "Test method matching in the server."
    http_mock.reset()
    add_test_preset()

    response = fake_client.get(url='/fred/test/another')
    assert_equals(response.status, 404)

    historical_call = http_mock.get_request(0)

    assert_equals(historical_call.method, 'GET')
    assert_equals(historical_call.url, '/fred/test/another')
    assert_equals(historical_call.body, b'')


def test_url_query_string():
    http_mock.reset()
    add_test_preset()
    response = fake_client.get(url='/test/two?a=1&b=2')
    assert_equals(response.status, 404)

    historical_call = http_mock.get_request(0)
    assert_equals(historical_call.method, 'GET')
    assert_equals(historical_call.url, '/test/two?a=1&b=2')
    assert_equals(historical_call.body, b'')


def test_reset_results_in_subsequent_404():
    "Expect a 404 after resetting the client"
    http_mock.reset()
    response = fake_client.post(url='/fred/test/one', )
    assert_equals(response.status, 404)


def test_configure_multiple_rules_independent():
    """We get iterating responses with last one repeated.

    TODO:
        Sort out the server so that it returns url/method specific responses
        rather than depending on the order of the call.
    """
    http_mock.reset()
    http_mock.when('.* /test_200').reply(status=200)
    http_mock.when('.* /test_400').reply(status=400)
    http_mock.when('.* /test_500').reply(status=500)
    http_mock.when('.* /test_410').reply(status=410)

    for url, expected_status in [('/test_200', 200),
                                 ('/test_400', 400),
                                 ('/test_500', 500),
                                 ('/test_410', 410)]:
        response = fake_client.get(url=url)
        assert_equals(response.status, expected_status)

    # Do one more to show that it'll always be 404 from here on in:
    response = fake_client.post(url='/test_200')
    assert_equals(response.status, 404)


def test_configure_multiple_rules_url_match():
    """We get responses based on the url used.
    """
    http_mock.reset()
    http_mock.when('.* /test_500').reply(status=500)
    http_mock.when('.* /test_410').reply(status=410)
    http_mock.when('.* /test_200').reply(status=200)
    http_mock.when('.* /test_400').reply(status=400)

    for url, expected_status in [('/test_200', 200),
                                 ('/test_400', 400),
                                 ('/test_400', 404),
                                 ('/test_500', 500),
                                 ('/test_500', 404),
                                 ('/test_410', 410)]:
        response = fake_client.get(url=url)
        assert_equals(response.status, expected_status)


def test_method_matching():
    "Test that server matches methods correctly."
    http_mock.reset()
    http_mock.when('GET /test_get').reply(b'You tested a get', 200)
    http_mock.when('POST /test_post').reply(b'You tested a post', 201)
    http_mock.when('.* /test_star').reply(b'You tested a .*', 202)
    http_mock.when('.* /test_star').reply(b'You tested a .*', 202)
    http_mock.when('(PUT|POST) /test_put_or_post').reply(
            b'You tested a PUT or a POST',  203)

    # Only GET works when GET matched
    assert_equals(404, fake_client.post(url="/test_get").status)
    assert_equals(200, fake_client.get(url="/test_get").status)
    assert_equals(404, fake_client.get(url="/test_get").status)

    # Only POST works when POST matched
    assert_equals(404, fake_client.get(url="/test_post").status)
    assert_equals(201, fake_client.post(url="/test_post").status)
    assert_equals(404, fake_client.post(url="/test_post").status)

    # Any method works with .* as the method matched
    assert_equals(202, fake_client.get(url="/test_star").status)
    assert_equals(202, fake_client.post(url="/test_star").status)
    assert_equals(404, fake_client.post(url="/test_star").status)

    # PUT or POST work with (PUT|POST) as the method matched
    assert_equals(404, fake_client.get(url="/test_put_or_post").status)
    assert_equals(203, fake_client.post(url="/test_put_or_post").status)
    assert_equals(404, fake_client.post(url="/test_put_or_post").status)


def test_multiple_responses_for_a_url():
    "Test each url pattern can have a multitude of responses"
    http_mock.reset()
    http_mock.when('.* /test_url_pattern').reply(status=200)
    http_mock.when('.* /test_url_pattern_2').reply(status=201)
    http_mock.when('.* /test_url_pattern').reply(status=301)
    http_mock.when('.* /test_url_pattern').reply(status=410)

    for url, expected_status in [('/test_url_pattern', 200),
                                 ('/test_url_pattern', 301),
                                 ('/test_url_pattern', 410),
                                 ('/test_url_pattern_2', 201),
                                 ('/test_url_pattern', 404),
                                 ('/test_url_pattern_2', 404)]:
        response = fake_client.get(url=url)
        assert_equals(response.status, expected_status)


def test_regular_expression_matching():
    "Test with regular expression matching"
    url = r'^GET /something/([a-zA-Z0-9\-_]*)/?'
    http_mock.reset()
    for i in range(5):
        http_mock.when(url).reply(status=200)

    for url, expected_status in [('/something/fred', 200),
                                 ('/something/10dDf', 200),
                                 ('/something/bbcDDD', 200),
                                 ('/something/13Fdr', 200),
                                 ('/something/1', 200),
                                 ('/something/Aaaa', 404)]:
        response = fake_client.get(url=url)
        assert_equals(response.status, expected_status)


def test_blank_url_matches_anything():
    "A blank url matcher header matches any url"
    http_mock.reset()
    http_mock.when('POST').reply(status=200)
    response = fake_client.post(url='/some/strange/12121/string')
    assert_equals(response.status, 200)
    # Check subsequent call 404s
    response = fake_client.post(url='/some/strange/12121/string')
    assert_equals(response.status, 404)


def test_setup_reply_multiple_times():
    "A times argument can be used to reply multiple times for the same url."
    http_mock.reset()
    http_mock.when('POST').reply(status=202, times=3)
    for expected_status in [202, 202, 202, 404]:
        response = fake_client.post(url='/some/strange/12121/string')
        assert_equals(response.status, expected_status)


def test_setup_reply_forever():
    """``FOREVER`` should make the url always respond with the given response.

    Clearly this doesn't test that it will *always* return the response. It
    tests that it does at least do it for 10 requests though.
    """
    http_mock.reset()
    http_mock.when('POST').reply(status=202, times=FOREVER)
    for _ in range(10):
        response = fake_client.post(url='/some/strange/12121/string')
        assert_equals(response.status, 202)


def test_setup_with_zero_or_negative_times():
    "Test that with zero times we get a 404 for the mock requests"
    http_mock.reset()
    assert_raises(ConfigurationError,
                  http_mock.when('POST').reply, status=202, times=0)

    assert_raises(ConfigurationError,
                  http_mock.when('POST').reply, status=202, times=-2)


def test_missing_method_and_url_matches_anything():
    "Missing matcher headers match anything"
    http_mock.reset()
    http_mock.reply(b'Hello', 323)
    response = fake_client.post(url='/some/strange/12121/string')
    assert_equals(response.status, 323)


def test_start_http_pretender():
    """
    Test that the http client kicks off an server via a call to the boss.

    TODO: This will need updating when we change the server to return
    dynamic port configurations for the mock server.
    """
    new_mock = HTTPMock('localhost', 8000)
    assert_true(new_mock.pretend_access_point != "localhost:8000")
    assert_true(int(new_mock.pretend_access_point.split(':')[1])
                 in PRETEND_PORT_RANGE)
