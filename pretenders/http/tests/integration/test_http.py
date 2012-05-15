from nose.tools import assert_equals

from pretenders.http.client import Client

test_client = Client('localhost', 8000, 8000)


def add_test_preset(path='/fred/test/one',
                    status=200,
                    body='You tested fred well',
                    method="POST"):
    test_client.add_preset(match_path=path,
                           match_method=method,
                           response_status=status,
                           response_body=body)


def test_configure_request_and_check_values():
    "Requires a running pretender.http.server instance"
    test_client.reset_all()
    test_client.set_server_mode(path_match=False)
    add_test_preset()
    response = test_client._mock.post(url='/fred/test/one')
    assert_equals(response.status, 200)
    assert_equals(response.read(), b'You tested fred well')

    request = test_client.get_request(0)

    assert_equals(request.getheader('X-Pretend-Request-Method'), 'POST')
    assert_equals(request.getheader('X-Pretend-Request-Path'),
                  '/fred/test/one')
    assert_equals(request.read(), b'')


def test_perform_wrong_method_on_configured_url():
    "Expect this to fail until we implement method matching in the server."
    test_client.reset_all()
    test_client.set_server_mode(path_match=True)
    add_test_preset()
    response = test_client._mock.get(url='/fred/test/one')
    assert_equals(response.status, 405)

    historical_call = test_client.get_request(0)
    assert_equals(historical_call.getheader('X-Pretend-Request-Method'), 'GET')
    assert_equals(historical_call.getheader('X-Pretend-Request-Path'),
                  '/fred/test/one')
    assert_equals(historical_call.read(), b'')


def test_reset_results_in_subsequent_404():
    "Expect a 404 after resetting the client"
    test_client.reset_all()
    test_client.set_server_mode(path_match=False)
    response = test_client._mock.post(url='/fred/test/one', )
    assert_equals(response.status, 404)


def test_configure_multiple_rules_independent():
    """We get iterating responses with last one repeated.

    TODO:
        Sort out the server so that it returns url/method specific responses
        rather than depending on the order of the call.
    """
    test_client.set_server_mode(path_match=False)
    test_client.reset_all()
    add_test_preset('/test_200', 200, 'You tested a 200')
    add_test_preset('/test_400', 400, 'You tested a 400')
    add_test_preset('/test_500', 500, 'You tested a 500')
    add_test_preset('/test_410', 410, 'You tested a 410')

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
    test_client.set_server_mode(path_match=True)
    test_client.reset_all()
    add_test_preset('/test_500', 500, 'You tested a 500')
    add_test_preset('/test_410', 410, 'You tested a 410')
    add_test_preset('/test_200', 200, 'You tested a 200')
    add_test_preset('/test_400', 400, 'You tested a 400')

    for url, expected_status_in_sequence in [('/test_200', 200),
                                             ('/test_400', 400),
                                             ('/test_400', 400),
                                             ('/test_500', 500),
                                             ('/test_500', 500),
                                             ('/test_410', 410)
                                              ]:
        response = test_client._mock.post(url=url)
        assert_equals(response.status, expected_status_in_sequence)


def test_method_matching():
    "Test that server matches methods correctly."
    test_client.set_server_mode(path_match=True)
    test_client.reset_all()
    add_test_preset('/test_get', 200, 'You tested a get', 'GET')
    add_test_preset('/test_post', 201, 'You tested a post', 'POST')
    add_test_preset('/test_star', 202, 'You tested a *', '*')

    # Only GET works when GET matched
    assert_equals(200, test_client._mock.get(url="/test_get").status)
    assert_equals(405, test_client._mock.post(url="/test_get").status)

    # Only POST works when POTS matched
    assert_equals(201, test_client._mock.post(url="/test_post").status)
    assert_equals(405, test_client._mock.get(url="/test_post").status)

    # Any method works with * as the method matched
    assert_equals(202, test_client._mock.get(url="/test_star").status)
    assert_equals(202, test_client._mock.post(url="/test_star").status)
