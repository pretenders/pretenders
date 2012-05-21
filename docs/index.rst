.. Pretenders documentation master file, created by
   sphinx-quickstart on Thu May 17 21:58:02 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Pretenders's documentation!
======================================

Pretenders are Mocks for network applications. They are mainly designed to be
used in system integration tests or manual tests where there is a need to 
simulate the behaviour of third party software that is not necessarily under
your control.

Example usage
-------------

Start the server to listen on all network interfaces::

    $ python -m pretenders.http.server --host 0.0.0.0 --port 8000

HTTP mock in a test case::

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



Contents:

.. toctree::
   :maxdepth: 2

   intro
   http

Sources can be found at https://github.com/txels/pretenders

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

