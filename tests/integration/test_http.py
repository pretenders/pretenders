import socket

from nose.tools import assert_equals, assert_true, assert_raises
import requests

from pretenders.common.constants import FOREVER
from pretenders.common.exceptions import ConfigurationError
from pretenders.client.http import HTTPMock
from . import get_fake_client


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
    response, data = fake_client.post(url='/fred/test/one')
    assert_equals(response.status, 200)
    assert_equals(data, b'You tested fred well')

    request = http_mock.get_request(0)

    assert_equals(request.method, 'POST')
    assert_equals(request.url, '/fred/test/one')
    assert_equals(request.body, b'')


def test_perform_wrong_method_on_configured_url():
    "Test method matching in the server."
    http_mock.reset()
    add_test_preset()

    response, data = fake_client.get(url='/fred/test/another')
    assert_equals(response.status, 404)

    historical_call = http_mock.get_request(0)

    assert_equals(historical_call.method, 'GET')
    assert_equals(historical_call.url, '/fred/test/another')
    assert_equals(historical_call.body, b'')


def test_url_query_string():
    http_mock.reset()
    add_test_preset()
    response, data = fake_client.get(url='/test/two?a=1&b=2')
    assert_equals(response.status, 404)

    historical_call = http_mock.get_request(0)
    assert_equals(historical_call.method, 'GET')
    assert_equals(historical_call.url, '/test/two?a=1&b=2')
    assert_equals(historical_call.body, b'')


def test_reset_results_in_subsequent_404():
    "Expect a 404 after resetting the client"
    http_mock.reset()
    response, data = fake_client.post(url='/fred/test/one', )
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
        response, data = fake_client.get(url=url)
        assert_equals(response.status, expected_status)

    # Do one more to show that it'll always be 404 from here on in:
    response, data = fake_client.post(url='/test_200')
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
        response, data = fake_client.get(url=url)
        assert_equals(response.status, expected_status)


def test_get_presets():
    """Test we can get the presets back from the boss directly."""
    http_mock.reset()
    http_mock.when('.* /test_500').reply(status=500)
    http_mock.when('.* /test_410').reply(status=410)
    http_mock.when('.* /test_200').reply(status=200)

    response = requests.get('http://localhost:8000/preset/{0}'.format(
                            http_mock.pretend_access_point_id))
    presets = response.json()
    assert_equals(len(presets), 3)

    assert_equals(presets[0]['status'], 500)
    assert_equals(presets[0]['rule']['rule'], '.* /test_500')

    assert_equals(presets[1]['status'], 410)
    assert_equals(presets[1]['rule']['rule'], '.* /test_410')

    assert_equals(presets[2]['status'], 200)
    assert_equals(presets[2]['rule']['rule'], '.* /test_200')


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
    assert_equals(404, fake_client.post(url="/test_get")[0].status)
    assert_equals(200, fake_client.get(url="/test_get")[0].status)
    assert_equals(404, fake_client.get(url="/test_get")[0].status)

    # Only POST works when POST matched
    assert_equals(404, fake_client.get(url="/test_post")[0].status)
    assert_equals(201, fake_client.post(url="/test_post")[0].status)
    assert_equals(404, fake_client.post(url="/test_post")[0].status)

    # Any method works with .* as the method matched
    assert_equals(202, fake_client.get(url="/test_star")[0].status)
    assert_equals(202, fake_client.post(url="/test_star")[0].status)
    assert_equals(404, fake_client.post(url="/test_star")[0].status)

    # PUT or POST work with (PUT|POST) as the method matched
    assert_equals(404, fake_client.get(url="/test_put_or_post")[0].status)
    assert_equals(203, fake_client.post(url="/test_put_or_post")[0].status)
    assert_equals(404, fake_client.post(url="/test_put_or_post")[0].status)


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
        response, data = fake_client.get(url=url)
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
        response, data = fake_client.get(url=url)
        assert_equals(response.status, expected_status)


def test_blank_url_matches_anything():
    "A blank url matcher header matches any url"
    http_mock.reset()
    http_mock.when('POST').reply(status=200)
    response, data = fake_client.post(url='/some/strange/12121/string')
    assert_equals(response.status, 200)
    # Check subsequent call 404s
    response, data = fake_client.post(url='/some/strange/12121/string')
    assert_equals(response.status, 404)


def test_setup_reply_multiple_times():
    "A times argument can be used to reply multiple times for the same url."
    http_mock.reset()
    http_mock.when('POST').reply(status=202, times=3)
    for expected_status in [202, 202, 202, 404]:
        response, data = fake_client.post(url='/some/strange/12121/string')
        assert_equals(response.status, expected_status)


def test_setup_reply_forever():
    """``FOREVER`` should make the url always respond with the given response.

    Clearly this doesn't test that it will *always* return the response. It
    tests that it does at least do it for 10 requests though.
    """
    http_mock.reset()
    http_mock.when('POST').reply(status=202, times=FOREVER)
    for _ in range(10):
        response, data = fake_client.post(url='/some/strange/12121/string')
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
    response, data = fake_client.post(url='/some/strange/12121/string')
    assert_equals(response.status, 323)


def test_start_http_pretender():
    """
    Test that the http client continues to use the boss for mock calls.
    """
    new_mock = HTTPMock('localhost', 8000)
    assert_true(new_mock.pretend_access_point == "localhost:8000")


def test_multiple_http_mocks_independently_served():
    """
    Ask for two http mocks and set up different presets.
    Make calls against each.
    We should get the correct responses back.
    """
    http_mock_1 = HTTPMock('localhost', 8000)
    http_mock_2 = HTTPMock('localhost', 8000)
    fake_client_1 = get_fake_client(http_mock_1)
    fake_client_2 = get_fake_client(http_mock_2)
    http_mock_1.reset()
    http_mock_2.reset()

    http_mock_1.when('GET /test_mock1_get').reply(b'You tested a get', 201,
                                                  times=FOREVER)
    http_mock_2.when('GET /test_mock2_get').reply(b'You tested a get', 200,
                                                  times=FOREVER)

    assert_equals(201, fake_client_1.get(url="/test_mock1_get")[0].status)
    assert_equals(200, fake_client_2.get(url="/test_mock2_get")[0].status)

    # Check that they both 404 if used against the other url.
    assert_equals(404, fake_client_1.get(url="/test_mock2_get")[0].status)
    assert_equals(404, fake_client_2.get(url="/test_mock1_get")[0].status)


def test_header_matching_with_no_match_headers():
    """ Test the best match is returned when request has no headers """
    http_mock.reset()
    http_mock.when('GET /test-headers', headers={'Some-Header': 'A'}).reply(
        b'', status=400)
    http_mock.when('GET /test-headers').reply(b'', status=200)
    http_mock.when('GET /test-headers',
                   headers={'Another-Header': 'A'}).reply(b'', status=500)

    response, data = fake_client.get(url='/test-headers')

    assert_equals(response.status, 200)


def test_header_matching_with_match_headers():
    """ Test the best match is returned when request has a matching header """
    http_mock.reset()
    http_mock.when('GET /test-headers',
                   headers={'Some-Header': 'A'}).reply(b'', status=500)
    http_mock.when('GET /test-headers',
                   headers={'Another-Header': 'A'}).reply(b'', status=200)
    http_mock.when('GET /test-headers').reply(b'', status=400)

    response, data = fake_client.get(url='/test-headers',
                               headers={'Another-Header': 'A'})

    assert_equals(response.status, 200)


def test_etag_workflow():
    """ Test the mocking of a typical caching workflow using Etags. """
    http_mock.reset()
    http_mock.when(
        'GET /test-etag', headers={'If-None-Match': 'A12345'}).reply(
            b'', status=304, times=FOREVER)
    http_mock.when('GET /test-etag').reply(
        b'Test etag', status=200, headers={'Etag': 'A12345'}, times=FOREVER)

    # Requests without headers return an Etag header.
    response, data = fake_client.get(url='/test-etag')
    assert_equals(response.status, 200)
    assert_equals(response.getheader('Etag', None), 'A12345')

    # Requests using the Etag header from above in the If-None-Match header
    # receive a 304 Not Modified response
    response, data = fake_client.get(url='/test-etag',
                               headers={'If-None-Match': 'A12345'})
    assert_equals(response.status, 304)

    # ... and will continue to receive 304 responses.
    response, data = fake_client.get(url='/test-etag',
                               headers={'If-None-Match': 'A12345'})
    assert_equals(response.status, 304)


def test_list_history():
    """
    Test that we can get the history out of a mock with one call.
    Test that we get the same history out from the bottle view at the boss.
    """
    http_mock.reset()
    add_test_preset()
    assert_equals([], http_mock.get_request())

    fake_client.get(url='/call_one')
    fake_client.get(url='/call_two')
    fake_client.get(url='/call_three')

    historical_calls = http_mock.get_request()

    assert_equals(len(historical_calls), 3)
    assert_equals(historical_calls[0].url, '/call_one')
    assert_equals(historical_calls[1].url, '/call_two')
    assert_equals(historical_calls[2].url, '/call_three')

    response = requests.get('http://localhost:8000/history/{0}'.format(
                            http_mock.pretend_access_point_id))

    historical_calls = response.json()
    assert_equals(len(historical_calls), 3)
    assert_equals(historical_calls[0]['url'], '/call_one')
    assert_equals(historical_calls[1]['url'], '/call_two')
    assert_equals(historical_calls[2]['url'], '/call_three')


def test_reply_depending_on_body():
    http_mock.reset()
    http_mock.when('POST /hello', body=u'1.*').reply(b'First', times=FOREVER)
    http_mock.when('POST /hello', body=u'2.*').reply(b'Second', times=FOREVER)

    response, data = fake_client.post(url='/hello', body=u'123')
    assert_equals(data, b'First')

    response, data = fake_client.post(url='/hello', body=u'234')
    assert_equals(data, b'Second')

    response, data = fake_client.post(url='/hello', body=u'345')
    assert_equals(response.status, 404)


def test_mock_timeout_behaviour():
    timeout_fake_client = get_fake_client(http_mock, timeout=10)

    http_mock.reset()
    http_mock.when(
        'GET /test-long-process').reply(b'', status=200, times=FOREVER,
                                        after=20)
    assert_raises(socket.timeout,
                  timeout_fake_client.get,
                  url='/test-long-process')
