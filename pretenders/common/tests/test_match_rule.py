import base64

from nose.tools import assert_true, assert_false

from pretenders.common.http import MatchRule

DEFAULT_HEADERS = {
    'Content-Length': '10',
    'Content-Type': 'text/html',
    'Host': 'localhost',
    'Accept-Encoding': 'identity',
}


def create_request(rule, headers=None, body=''):
    request = {'rule': rule}

    use_headers = {}
    use_headers.update(DEFAULT_HEADERS)

    if headers:
        use_headers.update(headers)

    # Add other headers to make the tests more realistic
    request['headers'] = use_headers
    request['body'] = base64.b64encode(body.encode()).decode()
    return request


def test_is_match_basic():
    """ Test a basic matching method / url"""
    match_rule = MatchRule('GET /test-match')
    mock_request = create_request('GET /test-match')

    assert_true(match_rule.matches(mock_request))
    assert_true(match_rule.rule_matches(mock_request['rule']))


def test_is_match_basic_is_false():
    """ Test a basic non-matching method \ url """
    match_rule = MatchRule('GET /testxx-match')
    mock_request = create_request('GET /test-match')

    assert_false(match_rule.matches(mock_request))
    assert_false(match_rule.rule_matches(mock_request['rule']))


def test_is_match_regex():
    """ Test a matching regex """
    match_rule = MatchRule('GET /test-match/[0-9]{5}')
    mock_request = create_request('GET /test-match/12345')

    assert_true(match_rule.matches(mock_request))
    assert_true(match_rule.rule_matches(mock_request['rule']))


def test_is_match_regex_is_false():
    """ Test a non-matching regex """
    match_rule = MatchRule('GET /test-match/[0-9]{5}')
    mock_request = create_request('GET /test-match/12a45')

    assert_false(match_rule.matches(mock_request))
    assert_false(match_rule.rule_matches(mock_request['rule']))


def test_is_match_headers():
    """ Test a matching rule with matching headers """
    match_rule = MatchRule('GET /test-match', headers={'Etag': 'A123'})
    mock_request = create_request('GET /test-match', {'Etag': 'A123'})

    assert_true(match_rule.matches(mock_request))
    assert_true(match_rule.rule_matches(mock_request['rule']))
    assert_true(match_rule.headers_match(mock_request['headers']))


def test_is_match_headers_is_false():
    """ Test a matching rule with non-matching headers """
    match_rule = MatchRule(
        'GET /test-match', headers={'ETag': 'A123'}
    )
    mock_request = create_request('GET /test-match', {'ETag': 'XXXX'})

    assert_false(match_rule.matches(mock_request))
    assert_true(match_rule.rule_matches(mock_request['rule']))
    assert_false(match_rule.headers_match(mock_request['headers']))


def test_is_match_headers_with_extra_headers():
    """ Test a matching rule with an unmatched extra header """
    match_rule = MatchRule(
        'GET /test-match',
        headers={'ETag': 'A123', 'Another-Header': 'XX'}
    )
    mock_request = create_request('GET /test-match', {'ETag': 'A123'})

    assert_false(match_rule.matches(mock_request))
    assert_true(match_rule.rule_matches(mock_request['rule']))
    assert_false(match_rule.headers_match(mock_request['headers']))


def test_is_match_with_no_headers():
    """ Test a matching rule with no headers """
    match_rule = MatchRule('GET /test-match')
    mock_request = create_request('GET /test-match', {'Etag': 'A123'})

    assert_true(match_rule.matches(mock_request))
    assert_true(match_rule.rule_matches(mock_request['rule']))
    assert_true(match_rule.headers_match(mock_request['headers']))


def test_is_match_with_headers_and_no_request_headers():
    """ Test a matching rule with headers not in request """
    match_rule = MatchRule('GET /test-match', headers={'Etag': 'A123'})
    mock_request = create_request('GET /test-match')

    assert_false(match_rule.matches(mock_request))
    assert_true(match_rule.rule_matches(mock_request['rule']))
    assert_false(match_rule.headers_match(mock_request['headers']))


def test_is_match_body():
    """ Test matching against body """
    match_rule = MatchRule('GET /test-match', body='foo')
    mock_request_good = create_request('GET /test-match', body='foo')
    mock_request_bad = create_request('GET /test-match', body='bar')

    assert_true(match_rule.matches(mock_request_good))
    assert_false(match_rule.matches(mock_request_bad))


def test_is_match_data_url_encoded():
    """ Test match URLencoded form """
    match_rule = MatchRule('GET /test-match',
                           data={'one': 'first', 'two': 'second thing'})
    mock_request_good = create_request('GET /test-match',
                                       body='one=first&two=second%20thing')
    mock_request_bad = create_request('GET /test-match',
                                      body='none=first&two=second')

    assert_true(match_rule.matches(mock_request_good))
    assert_false(match_rule.matches(mock_request_bad))


def test_is_not_match_missing_form_field():
    """ Test match URLencoded form """
    match_rule = MatchRule('GET /test-match',
                           data={'one': 'first', 'two': 'second thing'})
    mock_request = create_request('GET /test-match',
                                  body='one=first')

    assert_false(match_rule.matches(mock_request))

def test_is_match_data_multipart():
    """ Test match multipart form """

    boundary = '----onetwothree'
    headers = {
        'Content-Type': 'multipart/form-data; boundary={}'.format(boundary)
    }

    lines = [
        boundary,
        'Content-disposition: form-data; name="one"',
        '',
        'first',
        boundary,
        'Content-disposition: form-data; name="two"',
        '',
        'second'
    ]
    body = "\n".join(lines)

    lines = [
        boundary,
        'Content-disposition: form-data; name="one"',
        '',
        'first',
        boundary,
        'Content-disposition: form-data; name="two"',
        '',
        'other'
    ]
    body_bad = "\n".join(lines)

    match_rule = MatchRule('GET /test-match',
                           data={'one': 'first', 'two': 'second'})
    mock_request_good = create_request('GET /test-match',
                                       body=body, headers=headers)
    mock_request_bad = create_request('GET /test-match',
                                      body=body_bad, headers=headers)

    assert_true(match_rule.matches(mock_request_good))
    assert_false(match_rule.matches(mock_request_bad))
