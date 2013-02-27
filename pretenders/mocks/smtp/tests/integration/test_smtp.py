import smtplib
from email.mime.text import MIMEText
from nose.tools import assert_equals

from pretenders.client.smtp import SMTPMock

smtp_mock = SMTPMock('localhost', 8000)


def send_dummy_email(from_email='test@test.com',
                     to_email='test@test.com',
                     subject='test',
                     content='some content'):
    # Create a text/plain message
    msg = MIMEText(content)

    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    s = smtplib.SMTP(smtp_mock.host, smtp_mock.pretend_port)
    s.sendmail(from_email, [to_email], msg.as_string())
    s.quit()


def test_check_sent_email_content():
    #raise SkipTest()
    smtp_mock.reset()
    from_email = 'pretenders_from@test.com'
    to_email = 'pretenders_to@test.com'
    subject = 'Test Email!!'
    content = "Hey, thought I'd send you a message"
    send_dummy_email(from_email, to_email, subject, content)
    email_message = smtp_mock.get_email(0)

    assert_equals(email_message['Subject'], subject)
    assert_equals(email_message['From'], from_email)
    assert_equals(email_message['To'], to_email)
    assert_equals(email_message.content, content)


def test_reset_works():
    #raise SkipTest()
    smtp_mock.reset()
    send_dummy_email()
    assert_equals(1, len(smtp_mock.get_emails()))
    # Now reset it and check it works
    smtp_mock.reset()
    assert_equals(0, len(smtp_mock.get_emails()))


def test_history_stores_multiple_emails():
    #raise SkipTest()
    smtp_mock.reset()
    send_dummy_email()
    assert_equals(1, len(smtp_mock.get_emails()))
    send_dummy_email()
    assert_equals(2, len(smtp_mock.get_emails()))


def test_check_sent_email_none_sent():
    smtp_mock.reset()
    email_message = smtp_mock.get_email(0)
    assert_equals(email_message, None)
