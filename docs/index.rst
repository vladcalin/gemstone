.. pymicroservice documentation master file, created by
    sphinx-quickstart on Fri Nov 25 14:52:22 2016.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Welcome to gemstone's documentation!
====================================


The **gemstone** library aims to provide an easy way to develop simple and scalable microservices by using
the asynchronous features of Python.

This library offers support for writing a microservice that:

- exposes a public Json RPC 2.0 HTTP API (see `The JSON RPC 2.0 specifications <http://www.jsonrpc.org/specification>`_ )
- can protect API access based on API token identification.
- can communicate with other microservices through the JSON RPC protocol.
- can communicate with other microservices through events (messages).

This documentation is structured in multiple parts:

- :ref:`overview-top` - General information to get you started
- :ref:`10-minutes-example` - A quick example that covers the basics.
- :ref:`howto-top` - A collection of mini guides of how to handle various situations.
- :ref:`reference-top` - The reference to the classes, functions, constants that can be used.


Table of contents:

.. toctree::
    :maxdepth: 2

    intro/index
    howto/index
    reference/index
    changes


.. todoList::

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

