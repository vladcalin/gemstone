The **pymicroservice** framework
================================

Motivation
----------

In the past years, the microservice-based architecture became very popular in the computing field. 
Although this architecture grew more and more popular, there are a few tools that can help an
individual to build such systems. The current alternatives are using [nameko](https://github.com/nameko/nameko) 
or by building a web application that acts like a microservice. I started developing this framework in order
to provide a tool for creating and managing such systems with ease, and that are capable of being specialized in
a certain role, be it entity management, data storage or just computing.

Example basic usage
-------------------
Write into a ``my_service.py`` file the following code:

```python

	from pymicroservice.core.microservice import PyMicroService, \
	    public_method, private_api_method
    
    
    class MyService(PyMicroService):
        name = "name.your.service"
        host = "127.0.0.1"
        port = 5000
    
        def __init__(self):
            self._values = {}
            super(MyService, self).__init__()
    
        @public_method
        def say_hello(self, name):
            return "hello {}".format(name)
    
        @private_api_method
        def say_private_hello(self, name):
            """
            Retrieves a value that was previously stored.
            """
            return "Private hello {0}".format(name)
    
        # Implement your token validation logic
        def api_token_is_valid(self, api_token):
            return api_token == "hello_world"
    
    
    if __name__ == '__main__':
        service = MyService()
        service.start()

```

or generate it by using the command
```
    pymicroservice-cli new_service MyNewServiceClassName my_service.py 
```

After running the ``my_service.py`` script, we will have a running microservice at
http://localhost:5000/api . In order to interact with it, we have to use
 the JSONRPC protocol as follows:
 
```
    POST /api
    {
        "jsonrpc": "2.0",
        "method": "say_hello",
        "params": {
            "name": "world"
        },
        "id": 1
    }
```

The response will be

```
    {
        "error": null,
        "id": 1,
        "response": "hello world"
    }
```

In order to access the private method, we have to include in the HTTP
request an ``X-Api-Token`` header with the value ``hello_world``, so that the
method ``api_token_is_valid`` will return ``True``.

Project status
--------------

There are some basic features, such as:

- service creation through basic method exposure
- method access through API tokens
- possibility to add custom handlers (see the Tornado documentation)
- possibility to use Tornado templates (see the Tornado documentation)
- possibility to use static files

TODO
----

See [./TODO.md]
