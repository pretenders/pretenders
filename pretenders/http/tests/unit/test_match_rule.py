from nose.tools import assert_equals, assert_true, assert_raises, assert_false

from pretenders.http import MatchRule

def test_is_match_basic():
    """ Test a basic matching method / url"""
    match_rule = MatchRule('GET /test-match')
    mock_request = {'rule': 'GET /test-match'}

    assert_true(match_rule.is_match(mock_request))

def test_is_match_basic_is_false():
    """ Test a basic non-matching method \ url """
    match_rule = MatchRule('GET /testxx-match')
    mock_request = {'rule': 'GET /test-match'}

    assert_false(match_rule.is_match(mock_request))

def test_is_match_regex():
    """ Test a matching regex """
    match_rule = MatchRule('GET /test-match/[0-9]{5}')
    mock_request = {'rule': 'GET /test-match/12345'}

    assert_true(match_rule.is_match(mock_request))

def test_is_match_regex_is_false():
    """ Test a non-matching regex """
    match_rule = MatchRule('GET /test-match/[0-9]{5}')
    mock_request = {'rule': 'GET /test-match/12a45'}

    assert_false(match_rule.is_match(mock_request))

def test_is_match_headers():
    """ Test a matching rule with matching headers """
    match_rule = MatchRule(
        'GET /test-match', headers={'Etag': 'A123'}
    )
    mock_request = {
        'rule': 'GET /test-match',
        'headers': {'Etag': 'A123'},
    }

    assert_true(match_rule.is_match(mock_request))

def test_is_match_headers_is_false():
    """ Test a matching rule with non-matching headers """
    match_rule = MatchRule(
        'GET /test-match', headers={'ETag': 'A123'}
    )
    mock_request = {
        'rule': 'GET /test-match',
        'headers': {'ETag': 'XXXX'},
    }

    assert_false(match_rule.is_match(mock_request))

def test_is_match_headers_with_extra_headers():
    """ Test a matching rule with an unmatched extra header """
    match_rule = MatchRule(
        'GET /test-match', 
        headers={'ETag': 'A123', 'Another-Header': 'XX'}
    )
    mock_request = {
        'rule': 'GET /test-match', 
        'headers': {'ETag': 'XXXX'},
    }

    assert_false(match_rule.is_match(mock_request))

def test_is_match_default_headers_only():
    """ 
    Test a matching rule does not match if the request includes extra headers
    which are not part of the match rule when default_headers_only=True.
    """
    match_rule = MatchRule('GET /test-match', default_headers_only=True)
    mock_request = {
        'rule': 'GET /test-match',
        'headers': {'Etag': 'A123'},
    }
    assert_false(match_rule.is_match(mock_request))

def test_is_match_not_default_headers_only():
    """ 
    Test a matching rule matches regardless of headers when 
    default_headers_only is False (which is the default)
    """
    match_rule = MatchRule('GET /test-match')
    mock_request = {
        'rule': 'GET /test-match',
        'headers': {'Etag': 'A123'},
    }
    assert_true(match_rule.is_match(mock_request))

def test_is_match_headers_and_default_headers_only_error():
    """ 
    Test that creating a MatchRule with both headers and default_headers_only 
    will raise ValueError exception.
    """
    assert_raises(
        ValueError, MatchRule, 'GET /error', {'Some-Header': 'AA'}, True
    )

