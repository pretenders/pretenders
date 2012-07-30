.. Pretenders documentation master file, created by
   sphinx-quickstart on Thu May 17 21:58:02 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pretenders: Configurable Fake Servers
=====================================

Pretenders are Mocks for network applications. They are mainly designed to be
used in system integration tests or manual tests where there is a need to
simulate the behaviour of third party software that is not necessarily under
your control.

Installation
------------

Simply type::

    $ pip install pretenders

Example usage
-------------

Start the server to listen on all network interfaces::

    $ python -m pretenders.http.server --host 0.0.0.0 --port 8000

HTTP mock in a test case
~~~~~~~~~~~~~~~~~~~~~~~~

.. code::

    from pretenders.http.client import HttpMock

    # Assume a running server
    # Initialise the mock client and clear all responses
    mock = HttpMock('localhost', 8000)

    # For GET requests to /hello reply with a body of 'Hello'
    mock.when('/hello', 'GET').reply('Hello')

    # For the next POST  or PUT to /somewhere, simulate a BAD REQUEST status code
    mock.when('/somewhere', '(POST|PUT)').reply(status=400)

    # For the next request (any method, any URL) respond with some JSON data
    mock.reply('{"temperature": 23}', headers={'Content-Type': 'application/json'})

    # Your code is exercised here
    ...

    # Verify requests your code made
    r = mock.get_request(0)
    assert_equal(r.method, 'GET')
    assert_equal(r.url, '/weather?city=barcelona')

SMTP mock in a test case
~~~~~~~~~~~~~~~~~~~~~~~~

.. code::

    # Create a mock smtp service
    smtp_mock = SMTPMock('localhost', 8000)

    # Get the port number that this is faking on and
    # assign as appropriate to config files that the system being tested uses
    settings.SMTP_HOST = "localhost:{0}".format(smtp_mock.pretend_port)

    # ...run functionality that should cause an email to be sent

    # Check that an email was sent
    email_message = smtp_mock.get_email(0)
    assert_equals(email_message['Subject'], "Thank you for your order")
    assert_equals(email_message['From'], "foo@bar.com")
    assert_equals(email_message['To'], "customer@address.com")
    assert_true("Your order will be with you" in email_message.content)


Source code
-----------

Sources can be found at https://github.com/txels/pretenders

Contributions are welcome.

Contents
========

.. toctree::
   :maxdepth: 2

   intro
   http


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

