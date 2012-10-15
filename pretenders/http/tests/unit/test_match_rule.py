from nose.tools import assert_equals, assert_true, assert_raises, assert_false

from pretenders.http import MatchRule

def test_is_match_basic():
    """ Test a basic matching method / url"""
    match_rule = MatchRule('GET /test-match')
    mock_request = {'match': {'rule': 'GET /test-match'}}

    assert_true(match_rule.is_match(mock_request))

def test_is_match_basic_is_false():
    """ Test a basic non-matching method \ url """
    match_rule = MatchRule('GET /testxx-match')
    mock_request = {'match': {'rule': 'GET /test-match'}}

    assert_false(match_rule.is_match(mock_request))

def test_is_match_regex():
    """ Test a matching regex """
    match_rule = MatchRule('GET /test-match/[0-9]{5}')
    mock_request = {'match': {'rule': 'GET /test-match/12345'}}

    assert_true(match_rule.is_match(mock_request))

def test_is_match_regex_is_false():
    """ Test a non-matching regex """
    match_rule = MatchRule('GET /test-match/[0-9]{5}')
    mock_request = {'match': {'rule': 'GET /test-match/12a45'}}

    assert_false(match_rule.is_match(mock_request))

def test_is_match_headers():
    """ Test a matching rule with matching headers """
    match_rule = MatchRule(
        'GET /test-match', headers={'Etag': 'A123'}
    )
    mock_request = {
        'match': {'rule': 'GET /test-match'},
        'headers': {'Etag': 'A123'},
    }

    assert_true(match_rule.is_match(mock_request))

def test_is_match_headers_is_false():
    """ Test a matching rule with non-matching headers """
    match_rule = MatchRule(
        'GET /test-match', headers={'ETag': 'A123'}
    )
    mock_request = {
        'match': {'rule': 'GET /test-match'},
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
        'match': {'rule': 'GET /test-match'}, 
        'headers': {'ETag': 'XXXX'},
    }

    assert_false(match_rule.is_match(mock_request))
