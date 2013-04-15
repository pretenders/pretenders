#!/usr/bin/env python
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

if __name__ == '__main__':
    from pretenders.server import pretender_app
    from flup.server.fcgi import WSGIServer
    WSGIServer(pretender_app).run()
