from nose.tools import assert_equals

from pretenders.http.client import Client

test_client = Client('localhost', 8000)


def add_test_preset(status=200, body='You tested fred well'):
    test_client.add_preset(match_path='/fred/test/one',
                           match_method='POST',
                           response_status=status,
                           response_body=body)


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
    assert_equals(request.read(), b'')


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
    assert_equals(response.status, 200)

    historical_call = test_client.get_request(0)
    assert_equals(historical_call.method, 'GET')
    assert_equals(historical_call.path, '/test/two?a=1&b=2')
    assert_equals(historical_call.body, b'')


def test_reset_results_in_subsequent_404():
    "Expect a 404 after resetting the client"
    test_client.reset_all()
    response = test_client._mock.post(url='/fred/test/one', )
    assert_equals(response.status, 404)


def test_configure_multiple_rules():
    """We get iterating responses with last one repeated.

    TODO:
        Sort out the server so that it returns url/method specific responses
        rather than depending on the order of the call.
    """
    add_test_preset(200, 'You tested a 200')
    add_test_preset(400, 'You tested a 400')
    add_test_preset(500, 'You tested a 500')
    add_test_preset(410, 'You tested a 410')

    for expected_status_in_sequence in [200, 400, 500, 410]:
        response = test_client._mock.post(url='/anything')
        assert_equals(response.status, expected_status_in_sequence)

    # Do one more to show that it'll always be 404 from here on in:
    response = test_client._mock.post(url='/anything')
    assert_equals(response.status, 404)
