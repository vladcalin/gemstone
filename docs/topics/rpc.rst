.. _rpc-communication:

RPC communication via JSON RPC 2.0
==================================

.. note::

    Check out the `JSONRPC 2.0 protocol specifications <http://www.jsonrpc.org/specification>`_ .

The implementation
------------------

The RPC functionality is provided by the :py:class:`gemstone.TornadoJsonRpcHandler`. It is important to
note that the methods are not executed in the main thread, but in a ``concurrent.features.ThreadPoolExecutor``.

In order to create a basic microservice, you have to create a class that inherits the
:py:class:`gemstone.MicroService` class as follows

::

    import gemstone

    class MyMicroService(gemstone.MicroService):

        name = "hello_world_service"
        ...

Check out the :py:class:`gemstone.MicroService` documentation or :ref:`creating-a-service`
for the available attributes

Public methods
--------------
TODO

Private methods
---------------

TODO

Interacting with the microservice
---------------------------------

TODO

Interacting with another microservice
-------------------------------------

TODO

FAQ
---

TODO
