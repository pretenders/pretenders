from nose.tools import assert_equals

from pretenders.http.client import HttpMock, SubClient


class FakeClient(SubClient):

    def get(self, url, *args, **kwargs):
        url = "{0}{1}".format(self.url, url)
        return self.http('GET', url=url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        url = "{0}{1}".format(self.url, url)
        return self.http('POST', url=url, *args, **kwargs)


http_mock = HttpMock('localhost', 8000)
fake_client = FakeClient('localhost:8000', '/mock')


def add_test_preset(url='/fred/test/one',
                    method="POST",
                    body='You tested fred well',
                    status=200):
    http_mock.when(url, method).reply(body, status)


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
    "Expect this to fail until we implement method matching in the server."
    http_mock.reset()
    add_test_preset()
    response = fake_client.get(url='/fred/test/one')
    assert_equals(response.status, 405)

    historical_call = http_mock.get_request(0)

    assert_equals(historical_call.method, 'GET')
    assert_equals(historical_call.url, '/fred/test/one')
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
    http_mock.when('/test_200').reply(status=200)
    http_mock.when('/test_400').reply(status=400)
    http_mock.when('/test_500').reply(status=500)
    http_mock.when('/test_410').reply(status=410)

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
    http_mock.when('/test_500').reply(status=500)
    http_mock.when('/test_410').reply(status=410)
    http_mock.when('/test_200').reply(status=200)
    http_mock.when('/test_400').reply(status=400)

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
    http_mock.when('/test_get', 'GET').reply('You tested a get', 200)
    http_mock.when('/test_post', 'POST').reply('You tested a post', 201)
    http_mock.when('/test_star', '.*').reply('You tested a .*', 202)
    http_mock.when('/test_star', '.*').reply('You tested a .*', 202)
    http_mock.when('/test_put_or_post', '(PUT|POST)').reply(
            'You tested a PUT or a POST',  203)

    # Only GET works when GET matched
    assert_equals(405, fake_client.post(url="/test_get").status)
    assert_equals(200, fake_client.get(url="/test_get").status)
    assert_equals(404, fake_client.get(url="/test_get").status)

    # Only POST works when POST matched
    assert_equals(405, fake_client.get(url="/test_post").status)
    assert_equals(201, fake_client.post(url="/test_post").status)
    assert_equals(404, fake_client.post(url="/test_post").status)

    # Any method works with .* as the method matched
    assert_equals(202, fake_client.get(url="/test_star").status)
    assert_equals(202, fake_client.post(url="/test_star").status)
    assert_equals(404, fake_client.post(url="/test_star").status)

    # PUT or POST work with (PUT|POST) as the method matched
    assert_equals(405, fake_client.get(url="/test_put_or_post").status)
    assert_equals(203, fake_client.post(url="/test_put_or_post").status)
    assert_equals(404, fake_client.post(url="/test_put_or_post").status)


def test_multiple_responses_for_a_url():
    "Test each url pattern can have a multitude of responses"
    http_mock.reset()
    http_mock.when('/test_url_pattern').reply(status=200)
    http_mock.when('/test_url_pattern_2').reply(status=201)
    http_mock.when('/test_url_pattern').reply(status=301)
    http_mock.when('/test_url_pattern').reply(status=410)

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
    url = r'^/something/([a-zA-Z0-9\-_]*)/?'
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
    http_mock.when(url='', method='POST').reply(status=200)
    response = fake_client.post(url='/some/strange/12121/string')
    assert_equals(response.status, 200)
    response = fake_client.post(url='/some/strange/12121/string')
    assert_equals(response.status, 404)


def test_missing_method_and_url_matches_anything():
    "Missing matcher headers match anything"
    http_mock.reset()
    http_mock.reply(b'Hello', 323)
    response = fake_client.post(url='/some/strange/12121/string')
    assert_equals(response.status, 323)
