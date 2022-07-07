import time
from aiosmtpd.controller import Controller
import asyncore

from pretenders.server.log import get_logger
from pretenders.common.smtp import SMTPSerialiser
from pretenders.server.pretender import Pretender


LOGGER = get_logger('pretenders.server.mock_servers.smtp.server')

class MockSMTPHandler:

    def __init__(self, pretender):
        self.pretender = pretender

    async def handle_DATA(self, server, session, envelope):
        print("IN handle_DATA")
        data = envelope.content.decode('utf8', errors='replace')
        smtp_info = SMTPSerialiser(
            peer=session.peer, mailfrom=envelope.mail_from, rcpttos=envelope.rcpt_tos, data=data,
            rule='')
        body = smtp_info.serialize()
        LOGGER.info("Storing SMTP message: \n{0}".format(body))
        self.pretender.store_history_retrieve_preset(body)
        return '250 Message accepted for delivery'

class MockSMTPServer(Pretender):

    def run(self):
        "Runner for the MockSMTPServer"
        LOGGER.info(f"Running SMTP mock server on {self.host} {self.port}")
        controller = Controller(handler=MockSMTPHandler(self), hostname=self.host, port=self.port)
        try:
            controller.start()
            LOGGER.info("SMTP mock server started.")
            while True:
                # We sleep here, because the controller runs in a separate thread
                time.sleep(1)
        except KeyboardInterrupt:
            controller.stop()
        
    

if __name__ == "__main__":
    MockSMTPServer.start()
    
