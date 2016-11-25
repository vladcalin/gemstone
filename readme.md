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

I want to obtain a framework that will allow someone to develop a microservice in a manner similat to this
```python

	from pymicroservice.core.microservice import PyMicroService
from pymicroservice.core.decorators import public_method, private_api_method


class HelloWorldService(PyMicroService):
    name = "hello.world.service"
    host = "127.0.0.1"
    port = 5000

    def __init__(self):
        self._values = {}
        super(HelloWorldService, self).__init__()

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


if __name__ == '__main__':
    service = HelloWorldService()
    service.start()

```


Project status
--------------

This project is under heavy development.
