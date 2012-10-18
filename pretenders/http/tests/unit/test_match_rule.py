from nose.tools import assert_equals, assert_true, assert_raises, assert_false

from pretenders.http import MatchRule

DEFAULT_HEADERS = {
    'Content-Length': '10', 
    'Content-Type': 'text/html', 
    'Host': 'localhost', 
    'Accept-Encoding': 'identity',
}

NO_MATCH_SCORE = 0
RULE_ONLY_SCORE = 2
RULE_NO_HEADER_SCORE = 1
MATCHED_HEADER_SCORE = 2 + 1 

def create_request(rule, headers=None):
    request = {'rule': rule}
    if not headers:
        headers = {}
    headers.update(DEFAULT_HEADERS)
    request['headers'] = headers
    return request

def test_is_match_basic():
    """ Test a basic matching method / url"""
    match_rule = MatchRule('GET /test-match')
    mock_request = create_request('GET /test-match')

    assert_equals(
        match_rule.get_match_score(mock_request), RULE_ONLY_SCORE
    )

def test_is_match_basic_is_false():
    """ Test a basic non-matching method \ url """
    match_rule = MatchRule('GET /testxx-match')
    mock_request = create_request('GET /test-match')

    assert_equals(match_rule.get_match_score(mock_request), NO_MATCH_SCORE)

def test_is_match_regex():
    """ Test a matching regex """
    match_rule = MatchRule('GET /test-match/[0-9]{5}')
    mock_request = create_request('GET /test-match/12345')

    assert_equals(
        match_rule.get_match_score(mock_request), RULE_ONLY_SCORE
    )

def test_is_match_regex_is_false():
    """ Test a non-matching regex """
    match_rule = MatchRule('GET /test-match/[0-9]{5}')
    mock_request = create_request('GET /test-match/12a45')

    assert_equals(match_rule.get_match_score(mock_request), NO_MATCH_SCORE)

def test_is_match_headers():
    """ Test a matching rule with matching headers """
    match_rule = MatchRule('GET /test-match', headers={'Etag': 'A123'})
    mock_request = create_request('GET /test-match', {'Etag': 'A123'})

    assert_equals(match_rule.get_match_score(mock_request), MATCHED_HEADER_SCORE)

def test_is_match_headers_is_false():
    """ Test a matching rule with non-matching headers """
    match_rule = MatchRule(
        'GET /test-match', headers={'ETag': 'A123'}
    )
    mock_request = create_request('GET /test-match',{'ETag': 'XXXX'})

    assert_equals(match_rule.get_match_score(mock_request), RULE_NO_HEADER_SCORE)

def test_is_match_headers_with_extra_rule_headers():
    """ Test a matching rule with an unmatched extra header """
    match_rule = MatchRule(
        'GET /test-match', 
        headers={'ETag': 'A123', 'Another-Header': 'XX'}
    )
    mock_request = create_request('GET /test-match', {'ETag': 'XXXX'})

    assert_equals(match_rule.get_match_score(mock_request), RULE_NO_HEADER_SCORE)

def test_is_match_with_exact_headers_and_extra_request_headers():
    """ 
    Test score when a match with only a rule receives a match with
    additional headers.
    """
    match_rule = MatchRule('GET /test-match')
    mock_request = create_request('GET /test-match', {'Etag': 'A123'})
    
    assert_equals(match_rule.get_match_score(mock_request), RULE_ONLY_SCORE)

def test_is_match_with_exact_headers_and_no_request_headers():
    """ 
    Test score when a match with headers receives a request without headers 
    """
    match_rule = MatchRule('GET /test-match', headers={'Etag': 'A123'})
    mock_request = create_request('GET /test-match')
    
    assert_equals(match_rule.get_match_score(mock_request), RULE_NO_HEADER_SCORE)

def test_is_match_without_exact_headers_and_no_match_headers():
    """ 
    Test score when a match with only a rule receives a request with extra headers 
    """
    match_rule = MatchRule('GET /test-match')
    mock_request = create_request('GET /test-match', {'Etag': 'A123'})
    
    assert_equals(match_rule.get_match_score(mock_request), RULE_ONLY_SCORE)

