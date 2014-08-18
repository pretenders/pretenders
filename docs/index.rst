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

    $ python -m pretenders.server.server --host 0.0.0.0 --port 8000

HTTP mock in a test case
~~~~~~~~~~~~~~~~~~~~~~~~

Sample HTTP mocking test case::

    from pretenders.client.http import HTTPMock
    from pretenders.constants import FOREVER

    # Assume a running server
    # Initialise the mock client and clear all responses
    mock = HTTPMock('localhost', 8000)

    # For GET requests to /hello reply with a body of 'Hello'
    mock.when('GET /hello').reply('Hello', times=FOREVER)

    # For the next three POST or PUT to /somewhere, simulate a BAD REQUEST status code
    mock.when('(POST|PUT) /somewhere').reply(status=400, times=3)

    # For the next request (any method, any URL) respond with some JSON data
    mock.reply('{"temperature": 23}', headers={'Content-Type': 'application/json'})

    # For the next GET request to /long take 100 seconds to respond.
    mock.when('GET /long').reply('', after=100)

    # If you need to reply different data depending on request body
    # Regular expression to match certain body could be provided
    mock.when('POST /body_requests', body='1.*').reply('First answer', times=FOREVER)
    mock.when('POST /body_requests', body='2.*').reply('Second answer', times=FOREVER)

    # Your code is exercised here, after setting up the mock URL
    myapp.settings.FOO_ROOT_URL = mock.pretend_url
    ...

    # Verify requests your code made
    r = mock.get_request(0)
    assert_equal(r.method, 'GET')
    assert_equal(r.url, '/weather?city=barcelona')

HTTP mocking for remote application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes it is not possible to alter the settings of a running remote
application on the fly. In such circumstances you need to have a predetermined
url to reach the http mock on so that you can configure correctly ahead of
time.

Let's pretend we have a web app that on a page refresh gets data from an
external site. We might write some tests like::

    from pretenders.client.http import HTTPMock
    from pretenders.constants import FOREVER

    mock = HTTPMock('my.local.server', 9000, timeout=20, name="third_party")

    def setup_normal():
        mock.reset()
        mock.when("GET /important_data").reply(
            '{"account": "10000", "outstanding": "10.00"}',
            status=200,
            times=FOREVER)

    def setup_error():
        mock.reset()
        mock.when("GET /important_data").reply('ERROR', status=500, times=FOREVER)


    @with_setup(setup_normal)
    def test_shows_account_information_correctly():
        # Get the webpage
        ...
        # Check that the page shows things correctly as we expect.
        ...

    @with_setup(setup_error)
    def test_application_handles_error_from_service():
        # Get the webpage
        ...
        # Check that the page gracefully handles the error that has happened
        # in the background.
        ...

If you have a test set like the one above you know in advance that your app
needs to be configured to point to::

    http://my.local.server:9000/mockhttp/third_party

instead of the actual third party's website.


SMTP mock in a test case
~~~~~~~~~~~~~~~~~~~~~~~~

Sample SMTP mocking test case::

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

Sources can be found at https://github.com/pretenders/pretenders

Contributions are welcome.

Contents
========

.. toctree::
   :maxdepth: 2

   http


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

