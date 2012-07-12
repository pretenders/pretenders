from nose.tools import (
    assert_equals, assert_not_equals, assert_true, assert_false)
from mock import Mock

from pretenders.constants import PRETEND_PORT_RANGE
from pretenders.boss.apps.pretender import available_ports, PRETENDERS


def test_available_ports():
    """
    Test ``available_ports`` filters out ports that are in use by
    ``MOCK_SERVERS``.
    """
    ports = available_ports()

    assert_equals(ports, PRETEND_PORT_RANGE)

    mock_port = list(PRETEND_PORT_RANGE)[2]
    assert_true(mock_port in ports)
    # Now add a mock server

    pretend_server = Mock()
    pretend_server.port = mock_port
    PRETENDERS[1] = pretend_server

    # Now they should not be equal
    ports = available_ports()

    assert_not_equals(ports, PRETEND_PORT_RANGE)

    assert_false(mock_port in ports)
