import smtpd
import asyncore


class MockSMTPServer(smtpd.SMTPServer):

    def process_message(self, peer, mailfrom, rcpttos, data):
        print('Receiving message from:', peer)
        print('Message addressed from:', mailfrom)
        print('Message addressed to  :', rcpttos)
        print('Message length        :', len(data))
        return

server = MockSMTPServer(('127.0.0.1', 8001), None)

asyncore.loop()
