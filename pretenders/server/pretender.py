import argparse
import socket

from pretenders.server.base import (
    in_parent_process,
    save_pid_file)
from pretenders.server.log import get_logger
from pretenders.client import BossClient
from pretenders.common.constants import RETURN_CODE_PORT_IN_USE

LOGGER = get_logger('pretenders.server.pretender')


class Pretender(object):

    def __init__(self, uid, host, port, boss_port):
        self.uid = uid
        self.boss_port = boss_port
        self.host = host
        self.port = port
        self.boss_api_handler = BossClient(host, boss_port).boss_access

        if in_parent_process():
            save_pid_file('pretenders-mock-{0}.pid'.format(uid))

    def run(self):
        raise NotImplementedError(
            "run() not defined in {0}".format(self.__class__))

    @classmethod
    def start(cls):
        server = cls.from_command_line_args()
        try:
            server.run()
        except socket.error:
            LOGGER.info("QUITTING")
            import sys
            sys.exit(RETURN_CODE_PORT_IN_USE)

    @classmethod
    def from_command_line_args(cls):
        """Default parser for mock server scripts.

        Parse command line args and return the parsed object.
        """
        parser = argparse.ArgumentParser(description='Start the server')
        parser.add_argument(
            '-H', '--host', dest='host', default='localhost',
            help='host/IP to run the server on (default: localhost)')
        parser.add_argument(
            '-p', '--port', dest='port', type=int,
            default=8001, help=('port number to run the '
                                'server on (default: 8001)'))
        parser.add_argument(
            '-b', '--boss', dest='boss_port', default='8000',
            help="port for accessing the Boss server.")
        parser.add_argument(
            '-d', '--debug', dest="debug", default=False,
            action="store_true",
            help='start a build right after creation')
        parser.add_argument('-i', '--uid', dest='uid')
        args = parser.parse_args()
        return cls(uid=args.uid,
                   host=args.host,
                   port=args.port,
                   boss_port=args.boss_port)

    def store_history_retrieve_preset(self, body):
        return self.boss_api_handler.http(
            'POST',
            url="/replay/{0}".format(self.uid),
            body=body
        )
