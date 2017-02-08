Overview
========

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
