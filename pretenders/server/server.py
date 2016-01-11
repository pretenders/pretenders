import bottle

from pretenders.server.log import get_logger
from pretenders.server.base import in_parent_process, save_pid_file
from pretenders.server import data, pretender_app, settings
from pretenders.server.maintain import launch_maintainer

LOGGER = get_logger('pretenders.server.server')


def run(host='localhost', port=8000):
    "Start the mock HTTP server"
    data.BOSS_PORT = port
    if in_parent_process():
        if settings.RUN_MAINTAINER:
            LOGGER.debug('Starting maintainer process')
            launch_maintainer()
        save_pid_file('pretenders-boss.pid')

    bottle.run(app=pretender_app, host=host, port=port, reloader=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Start the server')
    parser.add_argument(
        '-H', '--host', dest='host', default='localhost',
        help='host/IP to run the server on (default: localhost)')
    parser.add_argument(
        '-p', '--port', dest='port', type=int, default=8000,
        help='port number to run the server on (default: 8000)')
    parser.add_argument(
        '-d', '--debug', dest="debug", default=False,
        action="store_true",
        help='set debug mode')
    parser.add_argument(
        '-t', '--timeout', dest='timeout', type=int,
        default=120,
        help='timeout before deleting stale pretenders')

    args = parser.parse_args()
    bottle.debug(args.debug)
    settings.TIMEOUT_PRETENDER = args.timeout
    LOGGER.debug('Setting pretender timeout: {0}'.format(args.timeout))
    run(args.host, args.port)
