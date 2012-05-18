from nose.tools import assert_equals

from pretenders.http.client import Client

test_client = Client('localhost', 8000)


def add_test_preset(match_path='/fred/test/one',
                    match_method="POST",
                    response_body='You tested fred well',
                    response_status=200,
                    ):
    test_client.add_preset(match_path=match_path,
                           match_method=match_method,
                           response_status=response_status,
                           response_body=response_body)


def test_configure_request_and_check_values():
    "Requires a running pretender.http.server instance"
    test_client.reset_all()
    add_test_preset()
    response = test_client._mock.post(url='/fred/test/one')
    assert_equals(response.status, 200)
    assert_equals(response.read(), b'You tested fred well')

    request = test_client.get_request(0)

    assert_equals(request.method, 'POST')
    assert_equals(request.path, '/fred/test/one')
    assert_equals(request.body, b'')


def test_perform_wrong_method_on_configured_url():
    "Expect this to fail until we implement method matching in the server."
    test_client.reset_all()
    add_test_preset()
    response = test_client._mock.get(url='/fred/test/one')
    assert_equals(response.status, 405)

    historical_call = test_client.get_request(0)

    assert_equals(historical_call.method, 'GET')
    assert_equals(historical_call.path, '/fred/test/one')
    assert_equals(historical_call.body, b'')


def test_url_query_string():
    test_client.reset_all()
    add_test_preset()
    response = test_client._mock.get(url='/test/two?a=1&b=2')
    assert_equals(response.status, 404)

    historical_call = test_client.get_request(0)
    assert_equals(historical_call.method, 'GET')
    assert_equals(historical_call.path, '/test/two?a=1&b=2')
    assert_equals(historical_call.body, b'')


def test_reset_results_in_subsequent_404():
    "Expect a 404 after resetting the client"
    test_client.reset_all()
    response = test_client._mock.post(url='/fred/test/one', )
    assert_equals(response.status, 404)


def test_configure_multiple_rules_independent():
    """We get iterating responses with last one repeated.

    TODO:
        Sort out the server so that it returns url/method specific responses
        rather than depending on the order of the call.
    """
    test_client.reset_all()
    add_test_preset('/test_200', response_status=200)
    add_test_preset('/test_400', response_status=400)
    add_test_preset('/test_500', response_status=500)
    add_test_preset('/test_410', response_status=410)

    for url, expected_status_in_sequence in [('/test_200', 200),
                                             ('/test_400', 400),
                                             ('/test_500', 500),
                                             ('/test_410', 410)]:
        response = test_client._mock.post(url=url)
        assert_equals(response.status, expected_status_in_sequence)

    # Do one more to show that it'll always be 404 from here on in:
    response = test_client._mock.post(url='/test_200')
    assert_equals(response.status, 404)


def test_configure_multiple_rules_path_match():
    """We get responses based on the path used.
    """
    test_client.reset_all()
    add_test_preset('/test_500', response_status=500)
    add_test_preset('/test_410', response_status=410)
    add_test_preset('/test_200', response_status=200)
    add_test_preset('/test_400', response_status=400)

    for url, expected_status_in_sequence in [('/test_200', 200),
                                             ('/test_400', 400),
                                             ('/test_400', 404),
                                             ('/test_500', 500),
                                             ('/test_500', 404),
                                             ('/test_410', 410)
                                              ]:
        response = test_client._mock.post(url=url)
        assert_equals(response.status, expected_status_in_sequence)


def test_method_matching():
    "Test that server matches methods correctly."
    test_client.reset_all()
    add_test_preset('/test_get', 'GET', 'You tested a get', 200)
    add_test_preset('/test_post', 'POST', 'You tested a post', 201)
    add_test_preset('/test_star', '.*', 'You tested a .*', 202)
    add_test_preset('/test_star', '.*', 'You tested a .*', 202)
    add_test_preset('/test_put_or_post', '(PUT|POST)',
            'You tested a PUT or a POST',  203)

    # Only GET works when GET matched
    assert_equals(405, test_client._mock.post(url="/test_get").status)
    assert_equals(200, test_client._mock.get(url="/test_get").status)
    assert_equals(404, test_client._mock.get(url="/test_get").status)

    # Only POST works when POST matched
    assert_equals(405, test_client._mock.get(url="/test_post").status)
    assert_equals(201, test_client._mock.post(url="/test_post").status)
    assert_equals(404, test_client._mock.post(url="/test_post").status)

    # Any method works with .* as the method matched
    assert_equals(202, test_client._mock.get(url="/test_star").status)
    assert_equals(202, test_client._mock.post(url="/test_star").status)
    assert_equals(404, test_client._mock.post(url="/test_star").status)

    # PUT or POST work with (PUT|POST) as the method matched
    assert_equals(405, test_client._mock.get(url="/test_put_or_post").status)
    assert_equals(203, test_client._mock.post(url="/test_put_or_post").status)
    assert_equals(404, test_client._mock.post(url="/test_put_or_post").status)


def test_multiple_responses_for_a_url():
    "Test each url pattern can have a multitude of responses"
    test_client.reset_all()
    add_test_preset('/test_url_pattern', response_status=200)
    add_test_preset('/test_url_pattern_2', response_status=201)
    add_test_preset('/test_url_pattern', response_status=301)
    add_test_preset('/test_url_pattern', response_status=410)

    for url, expected_status_in_sequence in [('/test_url_pattern', 200),
                                             ('/test_url_pattern', 301),
                                             ('/test_url_pattern', 410),
                                             ('/test_url_pattern_2', 201),
                                             ('/test_url_pattern', 404),
                                             ('/test_url_pattern_2', 404)
                                              ]:
        response = test_client._mock.post(url=url)
        assert_equals(response.status, expected_status_in_sequence)


def test_regular_expression_matching():
    "Test with regular expression matching"
    path = r'^/something/([a-zA-Z0-9\-_]*)/?'
    test_client.reset_all()
    for i in range(5):
        add_test_preset(path, response_status=200)

    for url, expected_status_in_sequence in [('/something/fred', 200),
                                             ('/something/10dDf', 200),
                                             ('/something/bbcDDD', 200),
                                             ('/something/13Fdr', 200),
                                             ('/something/1', 200),
                                             ('/something/Aaaa', 404),
                                              ]:
        response = test_client._mock.post(url=url)
        assert_equals(response.status, expected_status_in_sequence)


def test_blank_path_matches_anything():
    "A blank path matcher header matches any path"
    test_client.reset_all()
    add_test_preset("", response_status=200)
    response = test_client._mock.post(url='/some/strange/12121/string')
    assert_equals(response.status, 200)
    response = test_client._mock.post(url='/some/strange/12121/string')
    assert_equals(response.status, 404)


def test_missing_method_and_path_matches_anything():
    "Missing matcher headers match anything"
    test_client.reset_all()
    test_client.add_preset(response_status=323,
                           response_body=b'Hello')
    response = test_client._mock.post(url='/some/strange/12121/string')
    assert_equals(response.status, 323)
