Usage
=====


Basic example
-------------

In order to create a simple microservice, you have to subclass the :py:class:`pymicroservice.PyMicroService` base class:

::

    class HelloWorldService(PyMicroService):
        name = "hello.world.service"
        host = "127.0.0.1"
        port = 5000

        @public_method
        def say_hello(self, name):
            return "hello {}".format(name)

        @public_method
        def store_value(self, name, value):
            """
            Stores the value internally.
            """
            self._values[name] = value
            return "ok"

        @private_api_method
        def retrieve_value(self, name):
            """
            Retrieves a value that was previously stored.
            """
            return self._values[name]

        @public_method
        def more_stuff(self, x, y, k=3, *args, **kwargs):
            return "ok"

        def api_token_is_valid(self, api_token):
            return api_token == "test"


    if __name__ == '__main__':
        service = HelloWorldService()
        service.start()


In this example, we create a simple JSON RPC service that listens to ``127.0.0.1:5000`` and is available at
``http://127.0.0.1:5000/api``.

After that, we can access our microservice like this:

::

    curl -i -X UPDATE -H "Content-Type:application/json" -d \
    '{
      "jsonrpc": "2.0",
      "id": 1,
      "method": "say_hello",
      "args": {"name": "world"}
    }
    ' 'http://localhost:5000/api'



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
