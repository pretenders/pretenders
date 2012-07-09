from nose.tools import (
    assert_equals, assert_not_equals, assert_true, assert_false)
from mock import Mock

from pretenders.constants import MOCK_PORT_RANGE
from pretenders.boss.apps.mock_server import available_ports, HTTP_MOCK_SERVERS


def test_available_ports():
    """
    Test ``available_ports`` filters out ports that are in use by
    ``HTTP_MOCK_SERVERS``.
    """
    ports = available_ports()

    assert_equals(ports, list(MOCK_PORT_RANGE))

    assert_true(MOCK_PORT_RANGE[2] in ports)
    # Now add a mock server

    mock_server = Mock()
    mock_server.port = MOCK_PORT_RANGE[2]
    HTTP_MOCK_SERVERS[1] = mock_server

    # Now they should not be equal
    ports = available_ports()

    assert_not_equals(ports, list(MOCK_PORT_RANGE))

    assert_false(MOCK_PORT_RANGE[2] in ports)
