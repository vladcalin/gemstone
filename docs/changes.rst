Changes
=======

0.12.0 (22.04.2017)
~~~~~~~~~~~~~~~~~~~

- restructured modules
- bug fixes
- improved documentation
- improved tests

0.11.0 (08.04.2017)
~~~~~~~~~~~~~~~~~~~

- added ``Container.get_io_loop`` method
- added ``Container.get_executor`` method
- added ``RedisEventTransport``
- ``emit_event`` now emits just events. Removed the ``broadcast`` parameter.
  A task handling functionality will be added in a further version
- improved docs (still a work in progress)
- added some more tests (still a work in progress)


0.10.1 (27.03.2017)
~~~~~~~~~~~~~~~~~~~

- removed some forgotten debug messages


0.10.0 (23.03.2017)
~~~~~~~~~~~~~~~~~~~

- added ``broadcast`` parameter to ``MicroService.emit_event``
- added the ``broadcast`` parameter to ``BaseEventTransport.emit_event``
- added the ``broadcast`` parameter to ``RabbitMqEventTransport.emit_event``
- improved tests and documentation
- removed ``mappings`` and ``type`` parameters from ``Configurable``
- added ``gemstone.Module`` for better modularization of the microservice
- added ``gemstone.MicroService.authenticate_request`` method for a more flexible
  authentication mechanism
- deprecated ``gemstone.MicroService.api_token_is_valid`` method

0.9.0 (06.03.2017
~~~~~~~~~~~~~~~~~

- added the ``gemstone.exposed_method`` decorator for general usage that allows
    - to customize the name of the method
    - to specify if the method is a coroutine
    - to specify that the method requires a handler reference
    - to specify that the method is public or private
- deprecated
    - ``gemstone.public_method`` decorator
    - ``gemstone.private_api_method`` decorator
    - ``gemstone.async_method`` decorator
    - ``gemstone.requires_handler_reference`` decorator
- removed ``gemstone.MicroService.get_cli`` method in favor of the ``CommandLineConfigurator``
- improved documentation a little bit

0.8.0 (05.03.2017)
~~~~~~~~~~~~~~~~~~

- added the ``gemstone.requires_handler_reference`` decorator to enable
  the methods to get a reference to the Tornado request handler when called.
- added the ``gemstone.async_method`` decorator to make a method a coroutine
  and be able to execute things asynchronously on the main thread.
  For example, a method decorated with ``async_method`` will be able to
  ``yield self._executor.submit(make_some_network_call)`` without blocking the main
  thread.
- added two new examples:
    - ``example_coroutine_method`` - shows a basic usage if the ``async_method`` decorator
    - ``example_handler_ref`` - shows a basic usage if the ``requires_handler_reference`` decorator


0.7.0 (27.02.2017)
~~~~~~~~~~~~~~~~~~

- added ``gemstone.GemstoneCustomHandler`` class
- modified the way one can add custom Tornado handler to the microservice.
  Now these handlers must inherit ``gemstone.GemstoneCustomHandler``
- restructured docs, now it is based more on docstrings
- improved tests and code quality

0.6.0 (14.02.2017)
~~~~~~~~~~~~~~~~~~

- added configurable framework:
    - ``gemstone.config.configurable.Configurable`` class
    - ``gemstone.config.configurator.*`` classes
    - ``gemstone.MicroService.configurables`` and ``gemstone.MicroService.configurators`` attributes
    - switched testing to pytest
    - improved documentation (restructured and minor additions). Still a work in progress



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
