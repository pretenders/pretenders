from nose.tools import assert_equals, assert_true, assert_false
from mock import patch

from pretenders.http.client import CaseInsensitiveDict, SubClient


def test_caseinsensitivedict_creation():
    "Test case insensitivity after creation"
    test_dict = CaseInsensitiveDict({'MiXeD': 1,
                                     'lower': 2,
                                     'UPPER': 3})
    assert_equals(1, test_dict['mixed'])
    assert_equals(1, test_dict['MIXED'])
    assert_equals(1, test_dict['MIXed'])

    assert_equals(2, test_dict['lower'])
    assert_equals(2, test_dict['LOWER'])
    assert_equals(2, test_dict['LOWer'])

    assert_equals(3, test_dict['upper'])
    assert_equals(3, test_dict['UPPER'])
    assert_equals(3, test_dict['UPPer'])


def test_caseinsensitivedict_update():
    "Test case insensitivity after update"
    test_dict = CaseInsensitiveDict()

    test_dict['someKEY'] = 1

    assert_equals(1, test_dict['someKEY'])
    assert_equals(1, test_dict['SOMEkey'])
    assert_equals(1, test_dict['somekey'])


def test_caseinsensitivedict_raises_keyerror():
    "Test that if there isn't a case insensitive match a KeyError is raised"
    test_dict = CaseInsensitiveDict({'MiXeD': 1,
                                     'lower': 2,
                                     'UPPER': 3})
    key_error_raised = False
    try:
        test_dict['missing_key']
    except KeyError:
        key_error_raised = True
    assert_true(key_error_raised)


@patch('pretenders.http.client.HTTPConnection')
def test_subclient_connection_created_only_when_needed(HTTPConnection):
    "Test that the subclient connection is only created when needed."
    client = SubClient('localhost:8000', 'test')
    assert_false(HTTPConnection.called)
    # access the connection
    client.conn
    assert_equals(HTTPConnection.call_args, ('localhost:8000',))
