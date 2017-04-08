.. pymicroservice documentation master file, created by
    sphinx-quickstart on Fri Nov 25 14:52:22 2016.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Welcome to gemstone's documentation!
====================================


The **gemstone** library aims to provide an easy way to develop simple and
scalable microservices by using the asynchronous features of Python.

This library offers support for writing a microservice that:

- exposes a public Json RPC 2.0 HTTP API
  (see `The JSON RPC 2.0 specifications <http://www.jsonrpc.org/specification>`_ )
- can communicate with other microservices through the JSON RPC protocol.
- can communicate with other microservices through events (messages).

This documentation is structured in multiple parts:

- :ref:`topics-top` - A compilation in-depth explanations on various topics of interest.
- :ref:`reference-top` - The reference to the classes, functions, constants that can be used.


.. seealso::
    - JSON RPC 2.0 specifications: http://www.jsonrpc.org/specification
    - Tornado: http://www.tornadoweb.org/en/stable/

First look
----------

In a script ``hello_world.py`` write the following:

::

    import gemstone

    class HelloWorldService(gemstone.MicroService):
        name = "hello_world_service"
        host = "127.0.0.1"
        port = 8000

        @gemstone.exposed_method()
        def say_hello(self, name):
            return "hello {}".format(name)

    if __name__ == '__main__':
        service = HelloWorldService()
        service.start()

We have now a microservice that exposes a public method ``say_hello`` and returns
a ``"hello {name}"``.

What we did is the following:

- declared the class of our microservice by inheriting :py:class:`gemstone.MicroService`
- assigned a name for our service (this is required)
- assigned the ``host`` and the ``port`` where the microservice should listen
- exposed a method by using the :py:func:`gemstone.exposed_method` decorator.
- after that, when the script is directly executed, we start the service by calling
  the :py:meth:`gemstone.MicroService.start` method.

To run it, run script

::

    python hello_world.py

Now we have the service listening on ``http://localhost:8000/api`` (the default configuration
for the URL endpoint). In order to test it, you have to do a HTTP ``POST`` request to
that address with the content:

::

    curl -i -X POST \
       -H "Content-Type:application/json" \
       -d '{"jsonrpc": "2.0","id": 1,"method": "say_hello","params": {"name": "world"}}' \
     'http://localhost:8000/api'

The answer should be

::

    {"result": "hello world", "error": null, "jsonrpc": "2.0", "id": 1}



Table of contents:

.. toctree::
    :maxdepth: 2

    topics/index
    reference/index
    changes


.. todoList::

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

