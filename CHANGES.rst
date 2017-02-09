0.5.0 (09.02.2017)
~~~~~~~~~~~~~~~~~~

- added support for publisher-subscriber communication method:
    - base class for event transports: ``gemstone.event.transport.BaseEventTransport``
    - first concrete implementation: ``gemstone.event.transport.RabbitMqEventTransport``
    - ``gemstone.MicroService.emit_event`` for publishing an event
    - ``gemstone.event_handler`` decorator for designating event handlers
- restructured documentation (added tutorial, examples and howto sections).
- added asynchronous method calls in ``gemstone.RemoteService``.
- added ``gemstone.as_completed``, ``gemstone.first_completed``, ``gemstone.make_callbacks``
  utility functions for dealing with asynchronous method calls.


0.4.0 (25.01.2017)
~~~~~~~~~~~~~~~~~~

- modified ``accessible_at`` attribute of the ``gemstone.MicroService`` class
- added the ``endpoint`` attribute to the ``gemstone.MicroService`` class
- improved how the microservice communicates with the service registry

0.3.1 (25.01.2017)
~~~~~~~~~~~~~~~~~~

- fixed event loop freezing on Windows
- fixed a case when a ``TypeError`` was silenced when handling the bad parameters error
  in JSON RPC 2.0 handler (#21)
- major refactoring (handling of JSON RPC objects as Python objects instead of dicts and lists)
  to improve readability and maintainability
- improved documentation

0.3.0 (23.01.2017)
~~~~~~~~~~~~~~~~~~
- added validation strategies (method for extraction of api token from the request)
- base subclass for implementing validation strategies
- built in validation strategies: ``HeaderValidationStrategy``, ``BasicCookieStrategy``
- improved documentation


0.2.0 (17.01.2017)
~~~~~~~~~~~~~~~~~~

- added ``gemstone.RemoteService.get_service_by_name`` method
- added ``call`` command to cli
- added ``call_raw`` command to cli
- improved documentation a little

0.1.3 (16.01.2017)
~~~~~~~~~~~~~~~~~~

- fixed manifest to include required missing files

0.1.2 (16.01.2017)
~~~~~~~~~~~~~~~~~~

- added py36 to travis-ci
- refactored setup.py and reworked description files and documentation for better rendering

0.1.1 (13.01.2017)
~~~~~~~~~~~~~~~~~~

- changed the name of the library from ``pymicroservice`` to ``gemstone``
- added the ``gemstone.MicroService.accessible_at`` attribute

0.1.0 (09.01.2017)
~~~~~~~~~~~~~~~~~~

- added the ``pymicroservice.PyMicroService.get_cli`` method
- improved documentation a little bit

0.0.4
~~~~~

- fixed bug when sending a notification that would result in an error 
  was causing the microservice to respond abnormally (see #10)
- fixed a bug that was causing the service to never respond with the
  invalid parameters status when calling a method with invalid parameters

0.0.3
~~~~~

- added ``pymicroservice.RemoteService`` class
- added the ``pymicroservice.PyMicroService.get_service(name)``
- improved documentation
