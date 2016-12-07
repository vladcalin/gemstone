.. pymicroservice documentation master file, created by
    sphinx-quickstart on Fri Nov 25 14:52:22 2016.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Welcome to pymicroservice's documentation!
==========================================


The **pymicroservice** library aims to provide an easy way to
develop simple, understandable and scalable HTTP APIs by using
the asynchronous features of Python by using `Tornado <http://www.tornadoweb.org/en/stable/>`_ .

This library offers support for writing a microservice that:

- exposes a public Json RPC 2.0 HTTP API (see `The Jsonrpc 2.0 specifications <http://www.jsonrpc.org/specification>`_ )
- can protect API access based on API token identification
- can communicate with other microservices through JSONRPC.

.. warning::

    This project is under heavy development and is not ready for production use.


How it works
------------

This library uses the asynchronous features of the Tornado web framework for creating a JSON RPC endpoint through which
one can call exposed methods. The method calls are treated asynchronously. If you have no knowledge about asynchronous
programming in Python, I suggest to read a few words from the
`Tornado documentation <http://www.tornadoweb.org/en/stable/>`_ .

Basically, the steps in developing a microservice is:

1. you write a microservice class
2. you expose some methods to the public (in order to be called through the JSON RPC protocol)
3. you can define some static file directories (you can skip this).
4. you can add some extra Tornado handlers to handle various URLs (you can skip this).
5. you specify the service parameters (name, host, port and others)
6. based on the above steps, a Tornado application is generated with :py:class:`pymicroservice.TornadoJsonRpcHandler`
   handlers to handle POST requests at ``/api`` and with the custom handlers defined in step 4.


Contents:

.. toctree::
    :maxdepth: 2

    usage
    reference



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

