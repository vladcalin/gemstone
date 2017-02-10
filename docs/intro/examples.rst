.. _examples:

Examples
========

In the ``examples`` directory you can find some examples of microservices


#. ``example_client`` - an example usage of the :py:class:`gemstone.RemoteService` class for communication
   with microservices.

   There you will find two files: ``service.py`` and ``client.py``

   In ``service.py`` you have a basic microservice that exposes two methods: ``say_hello(name)`` and
   ``slow_method(seconds)``. You can start it with the command

   ::

        python service.py

   In ``client.py`` you can find some basic interaction with the service started above.

#. ``example_events`` - an example for the publisher-subscribe pattern in the microservice communication. There are
   two files: ``service.py`` and ``service2.py``. You can start them with the commands

   .. warning::

      You are going to need a RabbitMQ server running somewhere because the example uses it as message exchange transport

   ::

      python service.py
      python service2.py

   .. note::

         Those two commands must be executed in separate terminals/cmds because they are blocking.

   What happens here is:

   - the ``service.py`` subscribes to ``"said_hello"`` events.
   - the ``service2.py`` exposes a public method ``say_hello(name)``. When called, emits an ``"said_hello"`` event and then
     processes the request.

   After that, you can send a JSONRPC request to ``http://127.0.0.1:8000/api`` with the body

   ::

      {
         "jsonrpc": "2.0",
         "method": "say_hello",
         "params": {"name": "world"},
         "id": 1
      }

   and watch what happens.