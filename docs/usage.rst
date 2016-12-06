Usage
=====


Creating a microservice
-----------------------

In order to create a simple microservice, you have to subclass the :py:class:`pymicroservice.PyMicroService` base class:

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

Communicating with microservices through a :py:class:`pymicroservice.RemoteClient` instance
-------------------------------------------------------------------------------------------

This library provides a programmatic way to interact with microservices, through the
:py:class:`pymicroservice.RemoteClient`. In order to create an instance, we must know the location of the
service

::

    client = RemoteClient("http://127.0.0.1:5000/api")

    print(client.methods.say_hello("world"))  # "hello world"
    print(client.methods.say_private_hello("world"))  # raises pymicroservice.errors.CalledServiceError because we did not provide
                                                      # an api token

In order to be able to call private methods, we have to provide a valid api token in the initialisation step

::

    client = RemoteClient("http://127.0.0.1:5000/api", api_token="hello_world_token")
    print(client.methods.say_private_hello("world"))



The microservice specifications
-------------------------------

We can define various specifications for our microservice. The following class attributes can be overridden:

- :py:data:`pymicroservice.PyMicroService.name` - defines the name of the microservice. **MUST** be defined by the user
- :py:data:`pymicroservice.PyMicroService.host` - specifies the address to bind to (hostname or IP address). Defaults to ``127.0.0.1``.
- :py:data:`pymicroservice.PyMicroService.port` - an :py:class:`int` that specifies the port to bind to. Defaults to ``8000``
- :py:data:`pymicroservice.PyMicroService.api_token_header` - a :py:class:`str` that specifies the HTTP header that will be used for API access (See more in the next section).
- :py:data:`pymicroservice.PyMicroService.max_parallel_blocking_tasks` - the number of threads that will handle blocking actions (function calls). Defaults to :py:func:`os.cpu_count`.


Exposing public methods
-----------------------

In order to expose a public method, we have to decorate it with the :py:func:`pymicroservice.public_method` decorator, as seen
in the example.

Exposing private methods
------------------------

In order to expose a private method, we have to decorate it with the :py:func:`pymicroservice.private_api_method` decorator.
and override the :py:meth:`pymicroservice.PyMicroService.api_token_is_valid` method in order to validate the submitted api token.

When we want to call a private method, we have to include an extra HTTP header with the name denoted by
:py:data:`pymicroservice.PyMicroService.api_token_header` so that the :py:meth:`pymicroservice.PyMicroService.api_token_is_valid` method evaluates it to ``True``.
