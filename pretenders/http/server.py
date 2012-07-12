import bottle
from bottle import route, HTTPResponse

from pretenders.base import get_logger
from pretenders.base.pretender import Pretender
from pretenders.http import Preset, RequestSerialiser

LOGGER = get_logger('pretenders.http.server')


def get_header(header, default=None):
    return bottle.request.headers.get(header, default)


class MockHTTPServer(Pretender):

    def __init__(self, *args, **kwargs):
        super(MockHTTPServer, self).__init__(*args, **kwargs)
        self.setup_routes()

    def run(self):
        bottle.run(host=self.host, port=self.port, reloader=True)

    def setup_routes(self):
        route('<url:path>', method='ANY', callback=self.replay)

    def replay(self, url):
        """
        Replay a previously recorded preset, and save the request in history
        """
        request_info = RequestSerialiser(url, bottle.request)
        body = request_info.serialize()
        LOGGER.info("Replaying URL for request: \n{0}".format(body))
        boss_response = self.store_history_retrieve_preset(body)

        if boss_response.status == 200:
            preset = Preset(boss_response.read())
            return preset.as_http_response(bottle.response)
        else:
            LOGGER.error("Cannot find matching request\n{0}".format(body))
            raise HTTPResponse(boss_response.read(),
                               status=boss_response.status)


if __name__ == "__main__":
    MockHTTPServer.start()
