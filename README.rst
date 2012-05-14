PRETENDERS
==========

The pretenders project creates flexible fakes for external network services.
These external services can be faked by setting pre-canned answers,
defining expectations, or just querying them on received data after [test]
execution.

Pretenders will be written in Python3:

* Because it is about time
* Because since these will be standalone servers, compatibility is not such
  an issue

Initial goal for services to be mocked by pretenders: HTTP, SMTP


pretenders.http - HTTP server
-----------------------------

Typical usage is to mock RESTful/SOAP APIs of external services.
This will normally require pre-programming the service with responses,
and enquiring the service later about received queries. This can be done
with specialised assertions / matchers, or by setting expectations and
verifying fulfilment of such expectations.

The pre-programming step may be done by using specific proprietary HTTP
headers, or by using an alternative HTTP port to the one used for mocking.

Implementation is based on ``http.server.HTTPServer``

A client library will be provided to simplify interacting with the server.

pretenders.smtp - SMTP server
-----------------------------

Typical usage is to record a system's outgoing mail for further analysis.
No pre-programmed responses are necessary, just an API for checking
status and retrieving sent messages.

Implementation is based on ``smtpd.SMTPServer``
