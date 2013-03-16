# -*- coding: utf-8 -*-
from email.mime.text import MIMEText
from email.header import Header
import smtplib

from nose.tools import assert_equals

from pretenders.client.smtp import SMTPMock


smtp_mock = SMTPMock('localhost', 8000)


def send_dummy_email(from_email='test@test.com',
                     to_email='test@test.com',
                     subject='test',
                     content='some content'):
    # Create a text/plain message
    msg = MIMEText(content, 'plain', 'utf-8')

    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        s = smtplib.SMTP(smtp_mock.host, smtp_mock.pretend_port, timeout=10)
    except smtplib.SMTPServerDisconnected:
        # NOTE:
        # If this happens, make sure that your VM can actually ping things out
        # in the real world. I got this issue when I changed from wifi to
        # eth and the VM wasn't able to see anything. I think in such cases the
        # SMTP server cocks up.
        print("Server disconnected. There may be a bug in running the "
              "SMTP Mock server. Are you sure the boss managed to start "
              "it?")
        raise
    message = msg.as_string()
    s.sendmail(from_email, [to_email], message)
    s.quit()


def test_check_sent_email_content():
    smtp_mock.reset()
    from_email = 'pretenders_from@test.com'
    to_email = 'pretenders_to@test.com'
    subject = 'Test Email with óthér chárs ðöþæ!!'
    content = "Hey, thought I'd send you a message ðöþæ"
    send_dummy_email(from_email, to_email, subject, content)
    email_message = smtp_mock.get_email(0)

    assert_equals(email_message.subject, subject)
    assert_equals(email_message['From'], from_email)
    assert_equals(email_message['To'], to_email)
    assert_equals(email_message.content, content)


def test_reset_works():
    smtp_mock.reset()
    send_dummy_email()
    assert_equals(1, len(smtp_mock.get_emails()))
    # Now reset it and check it works
    smtp_mock.reset()
    assert_equals(0, len(smtp_mock.get_emails()))


def test_history_stores_multiple_emails():
    smtp_mock.reset()
    send_dummy_email()
    assert_equals(1, len(smtp_mock.get_emails()))
    send_dummy_email()
    assert_equals(2, len(smtp_mock.get_emails()))


def test_check_sent_email_none_sent():
    smtp_mock.reset()
    email_message = smtp_mock.get_email(0)
    assert_equals(email_message, None)
