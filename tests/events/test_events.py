import unittest.mock

import pytest

from gemstone.core import MicroService, event_handler
from gemstone.event.transport import BaseEventTransport


class MockedEventTransport(BaseEventTransport):
    register_event_handler = unittest.mock.MagicMock()
    on_event_received = unittest.mock.MagicMock()
    emit_event = unittest.mock.MagicMock()
    start_accepting_events = unittest.mock.MagicMock()


class SemiMockedEventTransport(BaseEventTransport):
    def __init__(self):
        self.handlers = {}

    def start_accepting_events(self):
        pass

    def register_event_handler(self, handler_func, handled_event_name):
        self.handlers[handled_event_name] = handler_func

    def on_event_received(self, event_name, event_body):
        self.handlers[event_name](event_body)

    def emit_event(self, event_name, event_body):
        pass


mocked_transport = MockedEventTransport()


class TestServicePublisher(MicroService):
    name = "test"

    event_transports = [
        mocked_transport
    ]

    handler = unittest.mock.MagicMock()
    # it is like a magic mock that is decorated
    handler = event_handler("test")(handler)


def test_event_handler_discovery():
    service = TestServicePublisher()
    service._gather_event_handlers()

    assert service.event_handlers == {"test": service.handler}


def test_transport_init():
    service = TestServicePublisher()
    service._gather_event_handlers()
    service._initialize_event_handlers()

    mocked_transport.register_event_handler.assert_has_calls([
        unittest.mock.call(service.handler, "test")
    ])


def test_transport_start_in_threads():
    service = TestServicePublisher()
    service.start_thread = unittest.mock.MagicMock()

    service._start_event_handlers()

    service.start_thread.assert_has_calls([
        unittest.mock.call(target=mocked_transport.start_accepting_events, args=(), kwargs={})
    ])


def test_emit_event():
    service = TestServicePublisher()

    service.emit_event("testing", "test_value")
    service.emit_event("testing2", "test_value2")

    mocked_transport.emit_event.assert_has_calls([
        unittest.mock.call("testing", "test_value"),
        unittest.mock.call("testing2", "test_value2")
    ])


def test_receive_event():
    transport = SemiMockedEventTransport()
    TestServicePublisher.event_transports = [transport]
    service = TestServicePublisher()
    service._gather_event_handlers()
    service._initialize_event_handlers()
    service._start_event_handlers()

    transport.on_event_received("test", "hello")

    service.handler.assert_has_calls([
        unittest.mock.call("hello")
    ])
