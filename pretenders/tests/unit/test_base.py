from nose.tools import assert_equals, assert_false
from mock import patch, call

from pretenders.base import SubClient


@patch('pretenders.base.HTTPConnection')
def test_subclient_connection_created_only_when_needed(HTTPConnection):
    "Test that the subclient connection is only created when needed."
    client = SubClient('localhost:8000', 'test')
    assert_false(HTTPConnection.called)
    # access the connection
    client.conn
    assert_equals(HTTPConnection.call_args, call('localhost:8000',))
