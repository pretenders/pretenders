import time

from nose.tools import assert_raises
import requests

from pretenders.common.exceptions import ConfigurationError
from pretenders.client.http import HTTPMock


def test_pretender_expired_add_preset_404():
    """
    Test that an expired pretender cannot have a preset assigned.

    This tries to test a race condition: The maintainer deletes expired
    Mocks. It does this by polling. Between polls, it is possible that a mock
    has expired and someone tries to apply a preset. In such a case, we should
    get a 404.
    """

    http_mock = HTTPMock('localhost', 8000, timeout=0.1)
    time.sleep(0.3)
    preset = http_mock.when('POST /fred/test/one')
    assert_raises(
        ConfigurationError, preset.reply, b'You tested fred well', 200
    )
