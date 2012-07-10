import smtpd
import asyncore

from pretenders.base import get_logger
from pretenders.base.mock_server import MockServer
from pretenders.smtp import SMTPSerialiser

LOGGER = get_logger('pretenders.http.server')


class MockSMTPServer(smtpd.SMTPServer, MockServer):

    def __init__(self, host, port, **kwargs):
        smtpd.SMTPServer.__init__(self, (host, port), None)
        MockServer.__init__(self, host=host, port=port, **kwargs)

    def process_message(self, peer, mailfrom, rcpttos, data):
        print('Receiving message from:', peer)
        print('Message addressed from:', mailfrom)
        print('Message addressed to  :', rcpttos)
        print('Message length        :', len(data))
        smtp_info = SMTPSerialiser(
            peer=peer, mailfrom=mailfrom, rcpttos=rcpttos, data=data)
        body = smtp_info.serialize()
        LOGGER.info("Replaying storing SMTP message: \n{0}".format(body))
        self.store_history_retrieve_preset(body)
        return

    def run(self):
        "Runner for the MockSMTPServer"
        asyncore.loop()


if __name__ == "__main__":
    MockSMTPServer.start()
