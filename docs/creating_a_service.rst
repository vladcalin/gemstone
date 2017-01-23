Creating a microservice
=======================


Basic example
-------------

In order to create a simple microservice, you have to subclass the :py:class:`gemstone.MicroService`
base class:

::

    class HelloWorldService(MicroService):
        name = "hello.world.service"
        host = "127.0.0.1"
        port = 5000

        @public_method
        def say_hello(self, name):
            return "hello {}".format(name)

        @private_api_method
        def say_private_hello(self, name):
            return "this is secret: hello {}".format(name)

        def api_token_is_valid(self, api_token):
            return api_token == "hello_world_token"


    if __name__ == '__main__':
        service = HelloWorldService()
        service.start()


After you created your service, run the script that contains it and enjoy.

Exposing public methods
~~~~~~~~~~~~~~~~~~~~~~~

Public methods can be exposed by decorating them with the :py:func:`gemstone.public_method` decorator

::

    class MyMicroService(MicroService):

        # stuff

        @public_method
        def exposed_public_method(self):
            return "it works!"

        # more stuff


Exposing private methods
~~~~~~~~~~~~~~~~~~~~~~~~

In order to expose private methods, we have to decorate them with the :py:func:`gemstone.private_api_method`.
These methods can be accessed only by providing a valid Api Token with the request. In addition, we must override the
:py:meth:`gemstone.MicroService.api_token_is_valid` method to implement the token validation logic

::

    class MyMicroService(MicroService):

        # stuff

        @private_api_method
        def exposed_private_method(self):
            return "it works!"

        def api_token_is_valid(self, api_token):
            return api_token == "correct_token"

        # more stuff



Customize the microservice
--------------------------

We can define various specifications for our microservice. The following class attributes can be overridden
to customize the behavior of our microservice.

Required attributes
~~~~~~~~~~~~~~~~~~~

- :py:data:`gemstone.MicroService.name` is required and defines the name of the microservice.
  **MUST** be defined by the concrete implementation, otherwise an error will be thrown at startup

Specifying different host and port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- :py:data:`gemstone.MicroService.host` - specifies the address to bind to (hostname or IP address).
  Defaults to ``127.0.0.1``.
- :py:data:`gemstone.MicroService.port` - an :py:class:`int` that specifies the port to bind to.
  Defaults to ``8000``
- :py:data:`gemstone.MicroService.accessible_at` - a (`address` : :py:class:`str`, `port` : :py:class:`int`) tuple
  specifying a custom location where the service can be found. If at least one service registry is configured,
  the service will send these values to it so that other services can access at the specified location.

  The `host` component can be a an address (`"127.0.0.1"`, `"192.168.0.3"`, etc) or a domain (if the service is
  accessible via DNS name. Example: `"myservice.example.com"`).

  For example, it is useful when the service runs behind a load balancer and the
  :py:data:`gemstone.MicroService.accessible_at` attribute will point to the address of the load balancer,
  so that when another service queries the registry for this service, it will access the
  load balancer instead. Also the first

Other options
~~~~~~~~~~~~~

- :py:data:`gemstone.MicroService.validation_strategies` - a list of validation strategy instances
  that will be used to extract the api token that will be forwarded to the :any:`MicroService.api_token_is_valid`
  method. Defaults to ``[HeaderValidationStrategy(header="X-Api-Token", template=None)]``

  See :ref:`token_validation` for more details, available options and how to implement custom validation
  strategies

  If multiple strategies are specified, they will be run in the order they are defined until the first one
  extracts a value which is not ``None``.

  In order to interact with a service that uses a validation strategy, we have to specify
  the proper arguments in the :py:class:`gemstone.RemoteService` constructor (See the class definition for more
  info on this).

  .. versionadded:: 0.3.0

- :py:data:`gemstone.MicroService.max_parallel_blocking_tasks` - the number of threads that
  will handle blocking actions (function calls). Defaults to :py:func:`os.cpu_count`.

Adding web application functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There might be situations when we want to extend the functionality of
the microservice so that it will display some stats on some pages (or other scenarios).
This library provides a way to quickly add behaviour that is not API-related.

- :py:data:`gemstone.MicroService.static_dirs` - a list of ``(str, str)`` tuples that represent the
  URL to which the static directory will be mapped, and the path of the directory that contain the static files.
  For example, if the directory ``/home/user/www/static`` contains the file ``index.html``, and we specify the static dir
  attribute with the value ``[("/static", "/home/user/www/static")]``, the service will serve ``index.html`` at the
  URL ``/static/index.html``.

- :py:data:`gemstone.MicroService.extra_handlers` - a list of tuples of URLs and Tornado request handlers to
  be included in the service.

  .. note::

        The ``/api`` endpoint is reserved for the JSON RPC service.

- :py:data:`gemstone.MicroService.template_dir` - a directory where templates will be searched in, when, in a
  custom handler we render a template via :py:meth:`tornado.web.RequestHandler.render`.


Periodic tasks
~~~~~~~~~~~~~~

- :py:data:`gemstone.MicroService.periodic_tasks` - a list of function - interval (in seconds) mappings that
  schedules the given function to be executed every given seconds

  ::

      def periodic_func():
          print("hello there")

      class MyService(MicroService):

          # stuff

          periodic_tasks = [(periodic_func, 1)]

          # stuff


  In te above example, the ``periodic_func`` will be executed every second.

  .. note::

        There might be a little delay in the execution of the function, depending on the main event loop availability.
        See `the Tornado documentation on PeriodicCallback  <http://www.tornadoweb.org/en/stable/ioloop.html#tornado.ioloop.PeriodicCallback>`_
        for more details.

  .. note::

        If you want to pass parameters to a function, you can use the :py:func:`functools.partial` to specify the
        parameters for the function to be called with.

Using a service registry
~~~~~~~~~~~~~~~~~~~~~~~~

A service registry is a remote service that keeps mappings of service names and network locations, so that each
microservice will be able to locate another one dynamically. A service can be a service registry if it exposes
via JSON RPC a ``ping(name, host, port)`` method and a ``locate_service(name)`` method.

- :py:data:`gemstone.MicroService.service_registry_urls` - a list of URLS where a service registry is located and
  accessible via JSON RPC.

  ::

      service_registry_urls = ["http://registry.domain.com:8000/api", "http://registry.domain2.com"]

  On service startup, a ping will be sent to the registry, and after that, a ping will be sent periodically.

- :py:data:`gemstone.MicroService.service_registry_ping_interval` - the interval (in seconds) when the
  service will ping the registry. Defaults to 30 seconds.

  ::

      service_registry_ping_interval = 120  # ping every two minutes


Generating a command-line interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See :py:meth:`gemstone.MicroService.get_cli()` for more details.
