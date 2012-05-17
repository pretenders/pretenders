HTTP Pretenders
===============

Mock HTTP server
----------------
The pretenders HTTP server provides 2 subsets of functionality:

* The configuration service, for pre-setting responses and reading back
  the recorded information. This is the part that your test code will
  interact with, or that you will be presetting manually, in the case of
  manual tests.
* The mocked or replay service, for regular operation (which plays back
  pre-set responses). This is the part that your application under test
  will talk to.

The configuration service
~~~~~~~~~~~~~~~~~~~~~~~~~
A RESTful service to pre-program responses or expectations.
Presets and History are exposed as resources. Typical HTTP methods are
accepted (POST to add element to collection, PUT to modify an element,
GET collection or element, DELETE collection or element).

What follows is a description of the server's *wire* protocol, i.e. at the
HTTP level.

Resource URLs:

* ``/preset/`` - the collection of presets
* ``/history/`` - the collection of recorded requests, where you can also
  target individual items, e.g.:

    * ``/history/0`` - the first recorded request
* ``/history/?url=&method=&status`` - matched recorded data

The presets contain all the information necessary to later produce a
pre-canned response. The mapping is as follows:

* response body = preset request body
* response status = preset header ``X-Pretend-Response-Status``
* response headers = all request headers, excluding those beginning with 
  ``X-Pretend-``

Preset responses are returned by the mock service in the order they have been
preset.

History will contain all requests that have been issued to the mock service.
History can be queried with HTTP GET, and responses will contain information
from the saved requests:

* The body will be the original request body
* The method used will be in a header ``X-Pretend-Request-Header``
* The (relative) URL will be in a header ``X-Pretend-Request-Path``

..
  * URL matcher (regex) = X-Pretend-Match-Url
  * HTTP methods to match = X-Pretend-Match-Methods (comma separated)

The mocked service
~~~~~~~~~~~~~~~~~~

Requests to the mocked service will return the preset responses in order.
All request information is then stored for future verification. Stored data
includes:

 * HTTP Method (GET, POST...)
 * Relative URL (``/city/association?n=12``)
 * HTTP Headers of the request
 * Body

