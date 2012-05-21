An Introduction to Pretenders
=============================

The ``pretenders`` project creates flexible fakes for external network
services. These external services can be faked by setting pre-canned answers,
defining expectations, or just querying them on received data after [test]
execution.

They are loosely designed along the pattern of Record/Replay/Verify.

The server side of Pretenders is written in Python3:

* Because I firmly believe all new projects should use Python3, unless 
  there are *very* compelling reasons against it.
* Because since these will be run as standalone servers, compatibility
  is not such an issue

In the cases we implement a client, we will be making this runnable in
Python 3.x and Python 2.6/2.7.

The initial service to be mocked by pretenders is HTTP.  
Future servers we are considering to support include SMTP and AMQP.
These they represent the vast majority of the services that the software we
write interacts with.

Some example use cases include:

* Mocking external HTTP-based APIs at the wire level in module integration tests
* Facilitating the manual testing and debugging of front-end Ajax code
  where the back-end has not been developed yet
* Writing fully automated tests for any system that sends email, and
  where we want to easily verify outgoing mails

Pretenders will provide a unified RESTful API to verify the interactions of
our code with external services, regardless of the service protocol.

pretenders.http - HTTP server
-----------------------------

Typical usage is to mock RESTful/SOAP APIs of external services.
This will normally require pre-programming the service with responses,
and enquiring the service later about received requests. This can be done
with specialised assertions / matchers, or by setting expectations and
verifying fulfilment of such expectations.

The pre-programming step may be done by using specific proprietary HTTP
headers, or by using an alternative HTTP port to the one used for mocking.

Implementation is based on the ``bottle`` web microframework.

One of our goals will be that the wire protocol is simple enough that you do
not need any specialised client. That said, we will be providing client
libraries (at least one in Python) to simplify interacting with the server,
and to provide a comfortable API to use in tests.
