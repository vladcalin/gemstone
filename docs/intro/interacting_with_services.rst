.. _interacting-with-services:

Interacting with services
=========================

There are a few methods to communicate with microservices. This framework, being written
around the JSON RPC protocol, allows microservices to be easily integrated with each other.

Through raw HTTP requests
-------------------------

First method to interact with a service is through raw HTTP requests. All you have to do is
making a ``POST`` request to ``http://service_ip:service_port/api`` with:

- the headers
    - ``Content-Type: application/json``

- the content

  ::

      {
        "jsonrpc": "2.0"
        "method": "the_name_of_the_method",
        "params": {
            "param_name": "value",
            "param_name_2": "value2"
        },
        "id": 1,
      }

  or

  ::

      {
        "jsonrpc": "2.0"
        "method": "the_name_of_the_method",
        "params": ["value1", "value2"],
        "id": 1,
      }

  If you want to send a notification (you don't care about the answer, don't include the ``"id"`` field in the
  request.

.. note::

    See the `JSON RPC 2.0 specifications <http://www.jsonrpc.org/specification>`_ for more details.

Through the :py:class:`gemstone.RemoteService` class
----------------------------------------------------------

This library offers the :py:class:`gemstone.RemoteService` class to interact with other
services programmatically.

Example ::

    client = RemoteService("http://127.0.0.1:5000/api")

    print(client.name)  # "hello.world.service"
    print(client.methods.say_hello("world"))  # "hello world"
    print(client.notifications.say_hello("world"))  # None -> we sent a notification, therefore discarding the result


In addition, this class provides a method to asynchronously call methods by passing
an extra keyword argument ``__async`` as shown in the following example

::

    async_response = client.methods.say_hello("world", __async=True)

    print(async_response)
    # <AsyncMethodCall ...>

    async_response.wait()
    print(async_response.finished())
    # True
    print(async_response.result())
    # "hello world"
    print(async_response.error())
    # None

.. seealso:: - :py:class:`gemstone.client.remote_service.AsyncMethodCall`,

             - :py:func:`gemstone.as_completed`,
             - :py:func:`gemstone.first_completed`
             - :py:func:`gemstone.make_callbacks`


Using a service registry
------------------------

We can configure a microservice to use a service registry. A service registry is a service that help services
identify other services without needing to know their exact location (services are identified by name).

A service registry can be a client that exposes via JSON RPC 2.0 the methods: ``ping(name, host, port)``
and ``locate_service(name)``.

In order for a service to make use of a service registry, we must override the
:py:data:`gemstone.MicroService.service_registry_urls` class attribute.

When we do that, a `periodic task <Periodic tasks>`_ will spawn when the service starts that calls the ``ping`` method
of the remote service, every :py:data:`gemstone.MicroService.service_registry_ping_interval` seconds.

.. note::

    A service can use multiple service registries. When multiple service registries are used, the service will
    send ``ping`` requests to all of them with the specified delay between them.

Example::

    class ExampleService(MicroService):
        name = "example.1"

        # stuff

        service_registries_urls = ["http://reg.hostname:5000/api", "http://reg.hostname2:8000/api"]

        # more stuff

        @public_method
        def say_hello(self, name):
            return "hello {}".format(name)

        # even more stuff

When at least one service registry is used, we can use the :py:meth:`gemstone.MicroService.get_service` method
to identify a service by name (or glob pattern). For example, if we call the method with the ``"myservice.workers.*"``
pattern, it will match ``"myservice.workers.01"``, ``"myservice.workers.02"`` and ``"myservice.workers.03"``.


Via the gemstone executable
---------------------------

We can interact with the ``gemstone`` executable using the ``call`` command:

::

    Usage: gemstone call [OPTIONS] NAME METHOD [PARAMS]...

    Options:
      --registry TEXT  The service registry URL used for queries
      --help           Show this message and exit.

The ``registry`` option specifies the URL where a service registry is accessible. For example: ``"http://192.168.0.1:8000/api"``.

- ``NAME`` - a glob pattern for the service you want to interact. Keep in mind that in the glob syntax, ``*`` matches
  a sequence of characters while ``?`` matches a single character.
- ``METHOD`` - the name of the method to call
- ``PARAMS`` - parameters for the call in the format ``name=value``. Current implementation supports only simple
  string values. In other words you can only send values in the format ``key=some_value`` that will be translated
  to ``func(key="some_value" ...)``. You can specify multiple parameters

Example::

    gemstone call --registry=http://localhost:8000/api servicename say_hello name=world
    # calls servicename.say_hello with the parameter name="world"

But if we want to interact with a service without having a service registry, we can use the ``call_raw`` command

::

    Usage: gemstone call_raw [OPTIONS] URL METHOD [PARAMS]...

    Options:
      --help  Show this message and exit.

- ``URL`` - a valid http(s) url where the service is located.
- ``METHOD`` - the name of the method to be called
- ``PARAMS`` - same as above

Example::

    gemstone.exe call_raw http://service.local/api get_service_specs
    [!] Service identification: 0.12918 seconds
    [!] Method call: 0.01701 seconds
    [!] Result:

    {'host': '0.0.0.0',
     'max_parallel_blocking_tasks': 4,
     ...