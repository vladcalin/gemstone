.. _rpc-communication:

RPC communication via JSON RPC 2.0
==================================

.. note::

    Check out the `JSONRPC 2.0 protocol specifications <http://www.jsonrpc.org/specification>`_ .

The implementation
------------------

The RPC functionality is provided by the :py:class:`gemstone.TornadoJsonRpcHandler`.
It is important to note that the blocking methods (that are not coroutines)
are not executed in the main thread, but in a ``concurrent.features.ThreadPoolExecutor``.
The methods that are coroutines are executed on the main thread.

In order to create a basic microservice, you have to create a class that inherits the
:py:class:`gemstone.MicroService` class as follows

::

    import gemstone

    class MyMicroService(gemstone.MicroService):

        name = "hello_world_service"
        ...

Check out the :py:class:`gemstone.MicroService` documentation for the available attributes

Public methods
--------------

Any method decorated with :py:func:``gemstone.exposed_method`` is a public method that
can be accessed by anybody.

Example exposed method:

::

    class MyMicroService(gemstone.MicroService):
        # ...

        @gemstone.exposed_method()
        def say_hello(self, world):
            return "hello {}".format(world)

        # ...

By default, a public method is blocking and will be executed in a threaded executor.

You can make an exposed method a coroutine as shown in the next example. From a coroutine you can
call other coroutines and can call blocking function by using the provided executor
(:py:meth:`gemstone.MicroService.get_executor`)

::

    class MyMicroService(gemstone.MicroService):
        # ...

        @gemstone.exposed_method(is_coroutine=True)
        def say_hello_coroutine(self, world):
            yield self.get_executor.submit(time.sleep, 3)
            return "hello {}".format(world)

        # ...

You can expose the public method under another name by giving the desired name as parameter
to the :py:func:`gemstone.exposed_method` decorator. The new name can even use dots!

::

    class MyMicroService(gemstone.MicroService):
        # ...

        @gemstone.exposed_method("myservice.say_hello")
        def ugly_name(self, world):
            return "hello {}".format(world)

        # ...


.. _private_methods:

Private methods
---------------

TODO

Interacting with the microservice
---------------------------------

Interaction with the microservice can be done by using the JSON RPC 2.0 protocol over HTTP.


.. _interacting_with_another_microservice:

Interacting with another microservice
-------------------------------------

Interaction with another microservice can be done by using the :py:class:`gemstone.RemoteService`
class. If at least one service registry was configured, you can use the
:py:meth:`gemstone.MicroService.get_service` method.

Or, as an alternative, if you know the exact network location of the remote service, you can
instantiate a :py:class:`gemstone.RemoteService` yourself

::

    remote_service = gemstone.RemoteService("http://10.0.0.1:8000/api")
    r = remote_service.call_method("say_hello", ("world",))
    print(r.result)
    # "hello world"

FAQ
---

TODO
