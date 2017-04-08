.. _publisher-subscriber:

Publisher-subscriber pattern
============================

In order to use the publisher-subscriber paradigm, you need to define at least one event transport

The currently implemented event transports are

- :py:class:`gemstone.event.transport.RabbitMqEventTransport`
- :py:class:`gemstone.event.transport.RedisEventTransport`

::

    class ExampleService(gemstone.MicroService):
        # ...
        event_transports = [
            gemstone.events.transport.RedisEventTransport("redis://127.0.0.1:6379/0"),
            gemstone.events.transport.RedisEventTransport("redis://redis.example.com:6379/0"),
            # ...
        ]
        # ...

After that, for publishing an event, you must call the :py:meth:`gemstone.MicroService.emit_event`
method

::

    @gemstone.exposed_method()
    def some_method(self):
        self.emit_event("test_event", {"message": "hello there"})
        self.emit_event("method_calls", {"method": "some_method"})
        # ...

In order to subscribe to some kind of events, you need to designate a method
as the event handler

::

    @gemstone.event_handler("test_event")
    def my_event_handler(self, event_body):
        self.logger.info("Received event: {}".format(event_body))


.. note::
    Event handler methods will be executed on the main thread, so they should not be
    blocking.
