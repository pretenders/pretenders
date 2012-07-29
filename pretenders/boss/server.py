import bottle

from pretenders import settings
from pretenders.base import get_logger, in_parent_process, save_pid_file
from pretenders.boss import data
from pretenders.boss.maintain import launch_maintainer
# Import apps so that they get initialised for bottle.
from pretenders.boss.apps import history, pretender, preset, replay


LOGGER = get_logger('pretenders.boss.server')


def run(host='localhost', port=8000):
    "Start the mock HTTP server"
    data.BOSS_PORT = port
    if in_parent_process():
        if settings.RUN_MAINTAINER:
            LOGGER.debug('Starting maintainer process')
            launch_maintainer()
        save_pid_file('pretenders-boss.pid')
    bottle.run(host=host, port=port, reloader=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Start the server')
    parser.add_argument('-H', '--host', dest='host', default='localhost',
                help='host/IP to run the server on (default: localhost)')
    parser.add_argument('-p', '--port', dest='port', type=int, default=8000,
                help='port number to run the server on (default: 8000)')
    parser.add_argument('-d', '--debug', dest="debug", default=False,
                action="store_true",
                help='start a build right after creation')

    args = parser.parse_args()
    bottle.debug(args.debug)
    run(args.host, args.port)
