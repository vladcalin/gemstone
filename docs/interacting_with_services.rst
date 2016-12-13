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
    - ``X-Api-Token: api-token`` if you want to access private methods

    .. note::

        The header might have another name, depending on the service configuration

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

Through the :py:class:`pymicroservice.RemoteService` class
----------------------------------------------------------

This library offers the :py:class:`pymicroservice.RemoteService` class to interact with other
services programmatically.

Example ::

    client = RemoteService("http://127.0.0.1:5000/api")

    print(client.name)  # "hello.world.service"
    print(client.methods.say_hello("world"))  # "hello world"
    print(client.notifications.say_hello("world"))  # None -> we sent a notification, therefore discarding the result


Using a service registry
------------------------

We can configure a microservice to use a service registry. A service registry is a service that help services
identify other services without needing to know their exact location (services are identified by name).

A service registry can be a client that exposes via JSON RPC 2.0 the methods: ``ping(name, host, port)``
and ``locate_service(name)``.

In order for a service to make use of a service registry, we must override the
:py:data:`pymicroservice.PyMicroService.service_registry_urls` class attribute.

When we do that, a `periodic task <Periodic tasks>`_ will spawn when the service starts that calls the ``ping`` method
of the remote service, every :py:data:`pymicroservice.PyMicroService.service_registry_ping_interval` seconds.

.. note::

    A service can use multiple service registries. When multiple service registries are used, the service will
    send ``ping`` requests to all of them with the specified delay between them.

Example::

    class ExampleService(PyMicroService):
        name = "example.1"

        # stuff

        service_registries_urls = ["http://reg.hostname:5000/api", "http://reg.hostname2:8000/api"]

        # more stuff

        @public_method
        def say_hello(self, name):
            return "hello {}".format(name)

        # even more stuff

When at least one service registry is used, we can use the :py:meth:`pymicroservice.PyMicroService.get_service` method
to identify a service by name (or glob pattern). For example, if we call the method with the ``"myservice.workers.*"``
pattern, it will match ``"myservice.workers.01"``, ``"myservice.workers.02"`` and ``"myservice.workers.03"``.
