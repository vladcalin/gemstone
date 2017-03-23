import unittest.mock
import pytest

from gemstone.event.transport.rabbitmq import RabbitMqEventTransport


def before_test_init(tr):
    tr.channel = unittest.mock.MagicMock()
    tr.channel.exchange_declare = unittest.mock.MagicMock()
    tr.channel.queue_declare = unittest.mock.MagicMock()
    tr.channel.queue_bind = unittest.mock.MagicMock()
    tr.channel.basic_consume = unittest.mock.MagicMock()
    tr.channel.start_consuming = unittest.mock.MagicMock()
    tr.channel.basic_reject = unittest.mock.MagicMock()
    tr.channel.basic_ack = unittest.mock.MagicMock()
    tr.channel.basic_publish = unittest.mock.MagicMock()
    tr.channel.close = unittest.mock.MagicMock()


@unittest.mock.patch("pika.BlockingConnection")
def test_add_handler(BlockingConnection):
    tr = RabbitMqEventTransport()
    before_test_init(tr)

    tr.register_event_handler(lambda x: print(x), "test")
    tr.register_event_handler(lambda x: print(x), "test2")
    tr.register_event_handler(lambda x: print(x), "test3")

    assert set(tr._handlers.keys()) == {"test", "test2", "test3"}


@unittest.mock.patch("pika.BlockingConnection")
def test_called_right_handler(BlockingConnection):
    tr = RabbitMqEventTransport()
    before_test_init(tr)
