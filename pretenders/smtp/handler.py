import datetime
import json
import os
import signal
import subprocess
import sys
import time

from pretenders.boss import PretenderModel
from pretenders.constants import (
    RETURN_CODE_PORT_IN_USE,
    PRETEND_PORT_RANGE
)
from pretenders.base import get_logger
from pretenders.boss import data
from pretenders.exceptions import NoPortAvailableException


LOGGER = get_logger('pretenders.smtp.handler')


class SMTPPretenderModel(PretenderModel):

    def __init__(self, start, uid, timeout, last_call, port, pid):
        super(SMTPPretenderModel, self).__init__(
            start, uid, timeout, last_call
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

    def new_pretender(self, uid, timeout, name):
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
                "pretenders.smtp.server",
                "-H", "localhost",
                "-p", str(port_number),
                "-b", str(data.BOSS_PORT),
                "-i", str(uid),
                ])
            time.sleep(2)  # Wait this long for failure
            process.poll()
            if process.returncode == RETURN_CODE_PORT_IN_USE:
                LOGGER.info("Return code already set. "
                            "Assuming failed due to socket error.")
                continue
            start = datetime.datetime.now()
            self.PRETENDERS[uid] = SMTPPretenderModel(
                start=start,
                port=port_number,
                pid=process.pid,
                timeout=datetime.timedelta(seconds=timeout),
                last_call=start,
                uid=uid,
            )
            LOGGER.info("Started smtp pretender on port {0}. uid {1}. pid {2}"
                        .format(port_number, uid, process.pid))
            return json.dumps({
                'full_host': "localhost:{0}".format(port_number),
                'id': uid})
        raise NoPortAvailableException("All ports in range in use")

    def delete_pretender(self, uid):
        "Delete a pretender by ``uid``"
        LOGGER.info("Performing delete on {0}".format(uid))
        pid = self.PRETENDERS[uid].pid
        LOGGER.info("attempting to kill pid {0}".format(pid))
        try:
            os.kill(pid, signal.SIGKILL)
            del self.PRETENDERS[uid]
        except OSError as e:
            LOGGER.info("OSError while killing:\n{0}".format(dir(e)))
