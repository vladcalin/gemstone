The **gemstone** framework
================================

![gemstones](./gemstones.png)

[![Build Status](https://travis-ci.org/vladcalin/gemstone.svg?branch=master)](https://travis-ci.org/vladcalin/gemstone)
[![Documentation Status](https://readthedocs.org/projects/gemstone/badge/?version=latest)](http://gemstone.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/gemstone.svg)](https://badge.fury.io/py/gemstone)
[![Coverage Status](https://coveralls.io/repos/github/vladcalin/gemstone/badge.svg?branch=master)](https://coveralls.io/github/vladcalin/gemstone?branch=master)

Motivation
----------

In the past years, the microservice-based architecture became very popular in the computing field. 
Although this architecture grew more and more popular, there are a few tools that can help an
individual to build such systems. The current alternatives are using [nameko](https://github.com/nameko/nameko) 
or by building a web application that acts like a microservice. I started developing this framework in order
to provide a tool for creating and managing such systems with ease, and that are capable of being specialized in
a certain role, be it entity management, data storage or just computing.

Few words ahead
---------------

This library uses the asynchronous features of the Tornado web framework for creating a JSON RPC endpoint through which
one can call exposed methods. The method calls are treated asynchronously. If you have no knowledge about asynchronous
programming in Python, I suggest to read a few words from the [Tornado documentation](http://www.tornadoweb.org/en/stable/) .

Although it is not required for you to know about all that coroutines and event loop theory, it sure helps to understand
what happens *under the hood*.

Installation
------------

In order to install this library, run the command

    pip install gemstone

or to install it from sources


    git clone https://github.com/vladcalin/gemstone.git
    cd gemstone
    python setup.py install

To run the tests, run the command

    python setup.py test


Example basic usage
-------------------
Write into a ``hello_world_service.py`` file the following code:

```python

    from gemstone import MicroService, public_method, private_api_method
	    
    
    
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

```

After running the ``hello_world_service.py`` script, we will have a running microservice at
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

This library offers a class through which you can interact with various services:

```python

    client = gemstone.RemoteClient("http://localhost:5000/api")
    print(client.name)  # "service.hello.world"
    print(client.methods.say_hello("world"))  # "hello world"
    
```


Issues
------

Check the [Github issue tracker](https://github.com/vladcalin/gemstone/issues).

TODO
----

See [TODO](TODO.md)

Collaborate
-----------

Any collaboration is welcome. Feel free to create new issues, make suggestions, open pull requests.

Changes
-------

See [CHANGES.md](CHANGES.md)

