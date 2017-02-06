The **gemstone** framework
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: https://badge.fury.io/py/gemstone.svg
    :target: https://badge.fury.io/py/gemstone
.. image:: https://travis-ci.org/vladcalin/gemstone.svg?branch=master
    :target: https://travis-ci.org/vladcalin/gemstone
.. image :: https://ci.appveyor.com/api/projects/status/i6rep3022e7occ8e?svg=true
    :target: https://ci.appveyor.com/project/vladcalin/gemstone
.. image:: https://readthedocs.org/projects/gemstone/badge/?version=latest
    :target: http://gemstone.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://coveralls.io/repos/github/vladcalin/gemstone/badge.svg?branch=master
    :target: https://coveralls.io/github/vladcalin/gemstone?branch=master
.. image:: https://codeclimate.com/github/vladcalin/gemstone/badges/gpa.svg
    :target: https://codeclimate.com/github/vladcalin/gemstone
    :alt: Code Climate
.. image:: https://landscape.io/github/vladcalin/gemstone/master/landscape.svg?style=flat
   :target: https://landscape.io/github/vladcalin/gemstone/master
   :alt: Code Health

Status
~~~~~~

This project is not ready for production use as it constantly receives improvements and it hasn't reached a mature enough phase to be declared stable.

It may receive further updates that break the backwards compatilibility. 


Motivation
~~~~~~~~~~

In the past years, the microservice-based architecture became very popular in the computing field. 
Although this architecture grew more and more popular, there are a few tools that can help an
individual to build such systems. The current alternatives are using `nameko <https://github.com/nameko/nameko>`_
or by building a web application that acts like a microservice. I started developing this framework in order
to provide a tool for creating and managing such systems with ease, and that are capable of being specialized in
a certain role, be it entity management, data storage or just computing.

Few words ahead
~~~~~~~~~~~~~~~

This library uses the asynchronous features of the Tornado web framework for creating a JSON RPC endpoint through which
one can call exposed methods. The method calls are treated asynchronously. If you have no knowledge about asynchronous
programming in Python, I suggest to read a few words from the `Tornado documentation <http://www.tornadoweb.org/en/stable/>`_ .

Although it is not required for you to know about all that coroutines and event loop theory, it sure helps to understand
what happens *under the hood*.

Installation
~~~~~~~~~~~~

In order to install this library, run the command ::

    pip install gemstone

or to install it from sources ::

    git clone https://github.com/vladcalin/gemstone.git
    cd gemstone
    python setup.py install

To run the tests, run the command ::

    python setup.py test


Example basic usage
~~~~~~~~~~~~~~~~~~~

Write into a ``hello_world_service.py`` file the following code:

::

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


After running the ``hello_world_service.py`` script, we will have a running microservice at
http://localhost:5000/api . In order to interact with it, we have to use the JSONRPC protocol as follows 

::

    POST /api
    {
        "jsonrpc": "2.0",
        "method": "say_hello",
        "params": {
            "name": "world"
        },
        "id": 1
    }
    
The response will be

::

    {
        "jsonrpc": "2.0",
        "error": null,
        "id": 1,
        "response": "hello world",
    }

In order to access the private method, we have to include in the HTTP
request an ``X-Api-Token`` header with the value ``hello_world``, so that the
method ``api_token_is_valid`` will return ``True`` (if the defaults configuration was kept).

This library offers a class through which you can interact programmatically with various services:

::

    client = gemstone.RemoteClient("http://localhost:5000/api")
    print(client.name)  # "service.hello.world"
    print(client.methods.say_hello("world"))  # "hello world"
    



Issues
~~~~~~

Check the `Github issue tracker <https://github.com/vladcalin/gemstone/issues>`_ .

Collaborate
~~~~~~~~~~~

Any collaboration is welcome. Feel free to create new issues, make suggestions, open pull requests.

Changes
~~~~~~~

See `CHANGES.MD` .
