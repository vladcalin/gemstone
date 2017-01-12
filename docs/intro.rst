Introduction
============

Installation
------------

In order to install this library, run the command

::

    pip install gemstone

or to install it manually from sources

::

    git clone https://github.com/vladcalin/gemstone.git
    cd gemstone
    python setup.py install

To run the tests, run the command

::

    python setup.py test


Few words ahead
---------------

This library uses the asynchronous features of the Tornado web framework for creating a JSON RPC endpoint through which
one can call exposed methods. The method calls are treated asynchronously. If you have no knowledge about asynchronous
programming in Python, I suggest to read a few words from the
`Tornado documentation <http://www.tornadoweb.org/en/stable/>`_ .

Although it is not required for you to know about all that coroutines and event loop theory, it sure helps to understand
what happens *under the hood*.

Simple usage
------------

In order to create a simple ``HelloWordService`` microservice, you have to subclass the
:py:class:`gemstone.MicroService` base class:

::

    # inside hello_world_service.py

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

Then, start the service with the command

::

    python hello_world_service.py

The server will start and will listen on http://localhost5000/api .

Issues
------

Check the `Github issue tracker <https://github.com/vladcalin/pymicroservice/issues>`_.


Collaborate
-----------

Any collaboration is welcome. Feel free to create new issues, make suggestions, open pull requests.
