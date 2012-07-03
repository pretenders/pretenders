from nose.tools import assert_equals, assert_false
from mock import patch, call, Mock

from pretenders.base import SubClient


def test_subclient_uses_connection_access_method_when_needed():
    "Test that the subclient connection is only created when needed."
    mock_conn_accessor = Mock()
    client = SubClient(mock_conn_accessor, 'test')
    assert_false(mock_conn_accessor.called)
    # access the connection
    client.conn
    assert_equals(mock_conn_accessor.call_args, call())
