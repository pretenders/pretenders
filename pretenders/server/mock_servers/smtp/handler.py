import datetime
import json
import os
import signal
import subprocess
import sys
import time

from pretenders.common.constants import (
    RETURN_CODE_PORT_IN_USE,
    PRETEND_PORT_RANGE
)
from pretenders.common.exceptions import NoPortAvailableException
from pretenders.server.log import get_logger

from pretenders.server import data
from pretenders.server.mock_servers import PretenderModel


LOGGER = get_logger('pretenders.server.mock_servers.smtp.handler')


class SMTPPretenderModel(PretenderModel):

    def __init__(self, start, name, timeout, last_call, port, pid):
        super(SMTPPretenderModel, self).__init__(
            start, name, timeout, last_call, protocol='smtp'
        )
        self.__dict__.update({
            'port': port,
            'pid': pid,
        })


class SmtpHandler(object):

    PRETENDERS = {}

    def available_ports(self):
        """
        Get a set of ports available for starting pretenders
        """
        ports_in_use = set(map(lambda x: x.port, self.PRETENDERS.values()))
        available_set = PRETEND_PORT_RANGE.difference(ports_in_use)
        return available_set

    def get_or_create_pretender(self, name, timeout):
        """
        Launch a new SMTP pretender in a separate process.

        It will first look for an available port.
        """
        for port_number in self.available_ports():
            LOGGER.info(
                "Attempt to start smtp pretender on port {0}, timeout {1}"
                .format(port_number, timeout))
            process = subprocess.Popen([
                sys.executable,
                "-m",
                "pretenders.server.mock_servers.smtp.server",
                "-H", "localhost",
                "-p", str(port_number),
                "-b", str(data.BOSS_PORT),
                "-i", str(name),
            ])
            time.sleep(2)  # Wait this long for failure
            process.poll()
            if process.returncode == RETURN_CODE_PORT_IN_USE:
                LOGGER.info("Return code already set. "
                            "Assuming failed due to socket error.")
                continue
            start = datetime.datetime.now()
            self.PRETENDERS[name] = SMTPPretenderModel(
                name=name,
                start=start,
                port=port_number,
                pid=process.pid,
                timeout=datetime.timedelta(seconds=timeout),
                last_call=start,
            )
            LOGGER.info("Started smtp pretender on port {0}. name {1}. pid {2}"
                        .format(port_number, name, process.pid))
            return json.dumps({
                'full_host': "localhost:{0}".format(port_number),
                'id': name})
        raise NoPortAvailableException("All ports in range in use")

    def delete_pretender(self, name):
        "Delete a pretender by ``name``"
        LOGGER.info("Performing delete on {0}".format(name))
        pid = self.PRETENDERS[name].pid
        LOGGER.info("attempting to kill pid {0}".format(pid))
        try:
            os.kill(pid, signal.SIGKILL)
            del self.PRETENDERS[name]
        except OSError as e:
            LOGGER.info("OSError while killing:\n{0}".format(dir(e)))
