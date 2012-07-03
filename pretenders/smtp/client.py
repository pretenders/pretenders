from pretenders.base import APIHelper


class SMTPMock(object):

    def __init__(self, host, port=9000):
        self.host = host
        self.port = port
        full_host = "{0}:{1}".format(self.host, self.port)
        self.history = APIHelper(full_host, '/history')

    def reset(self):
        "Call reset on the server"
        self.history.reset()

    def get_email(self, sequence_id=None):
        return dict(self.history.get(sequence_id))
