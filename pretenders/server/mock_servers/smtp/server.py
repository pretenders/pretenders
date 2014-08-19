import smtpd
import asyncore

from pretenders.server.log import get_logger
from pretenders.common.smtp import SMTPSerialiser
from pretenders.server.pretender import Pretender


LOGGER = get_logger('pretenders.server.mock_servers.smtp.server')


class MockSMTPServer(smtpd.SMTPServer, Pretender):

    def __init__(self, host, port, **kwargs):
        smtpd.SMTPServer.__init__(self, (host, port), None)
        Pretender.__init__(self, host=host, port=port, **kwargs)
        LOGGER.info("Initialised MockSMTPServer")

    def process_message(self, peer, mailfrom, rcpttos, data):
        smtp_info = SMTPSerialiser(
            peer=peer, mailfrom=mailfrom, rcpttos=rcpttos, data=data,
            rule='')
        body = smtp_info.serialize()
        LOGGER.info("Storing SMTP message: \n{0}".format(body))
        self.store_history_retrieve_preset(body)
        return

    def run(self):
        "Runner for the MockSMTPServer"
        LOGGER.info("Running SMTP mock server")
        asyncore.loop()


if __name__ == "__main__":
    MockSMTPServer.start()
    LOGGER.info("SMTP mock server started")
