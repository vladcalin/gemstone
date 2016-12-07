Usage
=====


Creating a microservice
-----------------------

In order to create a simple microservice, you have to subclass the :py:class:`pymicroservice.PyMicroService`
base class:

::

    class HelloWorldService(PyMicroService):
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


In order to create a template for your service, use the following command to create a HelloWorldService class inside a hello_world_service.py file

::

    pymicroservice-cli new_service HelloWorldService hello_world_service.py



After you created your service, run the script that contains it and enjoy.

Exposing public methods
~~~~~~~~~~~~~~~~~~~~~~~

Public methods can be exposed by decorating them with the :py:func:`pymicroservice.public_method` decorator

::

    class MyMicroService(PyMicroService):

        # stuff

        @public_method
        def exposed_public_method(self):
            return "it works!"

        # more stuff


Exposing private methods
~~~~~~~~~~~~~~~~~~~~~~~~

In order to expose private methods, we have to decorate them with the :py:func:`pymicroservice.private_api_method`.
These methods can be accessed only by providing a valid Api Token with the request. In addition, we must override the
:py:meth:`pymicroservice.PyMicroService.api_token_is_valid` method to implement the token validation logic

::

    class MyMicroService(PyMicroService):

        # stuff

        @private_api_method
        def exposed_private_method(self):
            return "it works!"

        def api_token_is_valid(self, api_token):
            return api_token == "correct_token"

        # more stuff


Communicating with microservices through HTTP requests
------------------------------------------------------

In the above example, we created a simple JSON RPC service that listens to ``127.0.0.1:5000`` and is available at
``http://127.0.0.1:5000/api``.

After that, we can access our microservice like this:

::

    curl -i -X POST -H "Content-Type:application/json" -d \
    '{
      "jsonrpc": "2.0",
      "id": 1,
      "method": "say_hello",
      "params": {"name": "world"}
    }
    ' 'http://localhost:5000/api'

The response should be

::

    {
        "jsonrpc": "2.0",
        "id": 1,
        "error": null,
        "result": "hello world"
    }

There are a few basic elements that are important in a JSONRPC request:

- the ``"jsonrpc"`` key that have the value of ``"2.0"`` in order to identify the protocol used for communication
- the ``"id"`` key that specifies that we wait for an answer. If the value is ``null`` or the key is missing, the server will treat the request as a notification and will return a dummy answer right away while continuing to process the function in background.
- the ``"method"`` key that specifies what method to call.
- the ``"params"`` key that specifies the parameters of the method call. The value can be a :py:class:`dict` with keyword parameters (ex: ``{"key1": "value1", "key2": "value2"}``, or an array with positional parameters (ex: ``["value1", "value2"]``).

In order to access the private method ``say_private_hello``, we have to include a secret ``X-Api-Token`` header in
our HTTP request

::

    curl -i -X POST -H "Content-Type:application/json"
    -H "X-Api-Token:hello_world_token" -d \
    '{
      "jsonrpc": "2.0",
      "id": 1,
      "method": "say_private_hello",
      "params": {"name": "world"}
    }
    ' 'http://localhost:5000/api'

The response should be

::

    {
        "jsonrpc": "2.0",
        "id": 1,
        "error": null,
        "result": "this is secret: hello world"
    }

If we do not include a correct api token or do not include an api token at all, calling a private method
will result in an ``Access denied`` error.

Communicating with microservices through a :py:class:`pymicroservice.RemoteService` instance
--------------------------------------------------------------------------------------------

This library provides a programmatic way to interact with microservices, through the
:py:class:`pymicroservice.RemoteService`. In order to create an instance, we must know the location of the
service

::

    client = RemoteService("http://127.0.0.1:5000/api")

    print(client.methods.say_hello("world"))  # "hello world"
    print(client.methods.say_private_hello("world"))  # raises pymicroservice.errors.CalledServiceError because we did not provide
                                                      # an api token

In order to be able to call private methods, we have to provide a valid api token in the initialisation step

::

    client = RemoteService("http://127.0.0.1:5000/api", api_token="hello_world_token")
    print(client.methods.say_private_hello("world"))



Customize the microservice
--------------------------

We can define various specifications for our microservice. The following class attributes can be overridden

Required attributes
~~~~~~~~~~~~~~~~~~~

- :py:data:`pymicroservice.PyMicroService.name` is required and defines the name of the microservice.
  **MUST** be defined by the concrete implementation, otherwise an error will be thrown at startup

Specifying different host and port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- :py:data:`pymicroservice.PyMicroService.host` - specifies the address to bind to (hostname or IP address).
  Defaults to ``127.0.0.1``.
- :py:data:`pymicroservice.PyMicroService.port` - an :py:class:`int` that specifies the port to bind to.
  Defaults to ``8000``

Other options
~~~~~~~~~~~~~

- :py:data:`pymicroservice.PyMicroService.api_token_header` - a :py:class:`str` that specifies the HTTP
  header that will be used for API access. Defaults to ``X-Api-Token``.

  In order to interact with a service that uses a custom ``api_token_header``, we have to specify it in the
  :py:class:`pymicroservice.RemoteService` constructor

  ::

        client = RemoteService(url, api_token="Custom-Token", api_key="my-api-key")

- :py:data:`pymicroservice.PyMicroService.max_parallel_blocking_tasks` - the number of threads that
  will handle blocking actions (function calls). Defaults to :py:func:`os.cpu_count`.


- :py:data:`pymicroservice.PyMicroService.static_dirs` - a list of ``(str, str)`` tuples that represent the
  URL to which the static directory will be mapped, and the path of the directory that contain the static files.
  For example, if the directory ``/home/user/www/static`` contains the file ``index.html``, and we specify the static dir
  attribute with the value ``[("/static", "/home/user/www/static")]``, the service will serve ``index.html`` at the
  URL ``/static/index.html``.

- :py:data:`pymicroservice.PyMicroService.extra_handlers` - a list of tuples of URLs and Tornado request handlers to
  be included in the service.

  .. note::

        The ``/api`` endpoint is reserved for the JSON RPC service.

- :py:data:`pymicroservice.PyMicroService.template_dir` - a directory where templates will be searched in, when, in a
  custom handler we render a template via :py:meth:`tornado.web.RequestHandler.render`.

