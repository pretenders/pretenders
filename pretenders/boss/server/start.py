import argparse

import bottle
from pretenders.boss.server import run


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
