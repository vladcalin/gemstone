import json

import pika

from gemstone.event.transport.base import BaseEventTransport


class RabbitMqEventTransport(BaseEventTransport):
    EXCHANGE_PREFIX_BROADCAST = "gemstone.broadcast."
    EXCHANGE_PREFIX_SINGLE = "gemstone.tasks."

    def __init__(self, host="127.0.0.1", port=5672, username="", password="", **connection_options):
        """
        Event transport via RabbitMQ server.

        :param host: ipv4 or hostname
        :param port: the port where the server listens
        :param username: username used for authentication
        :param password: password used for authentication
        :param connection_options: extra arguments that will be used in
                                   :py:class:`pika.BlockingConnection` initialization.
        """
        self._handlers = {}

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host, port=port,
                credentials=pika.PlainCredentials(username=username, password=password),
                **connection_options
            )
        )
        self.channel = self.connection.channel()

    def register_event_handler(self, handler_func, handled_event_name):
        self._handlers[handled_event_name] = handler_func

    def start_accepting_events(self):
        for event_name, event_handler in self._handlers.items():
            # prepare broadcast queues
            current_exchange_name = self.EXCHANGE_PREFIX_BROADCAST + event_name
            self.channel.exchange_declare(
                exchange=current_exchange_name,
                type="fanout"
            )
            result = self.channel.queue_declare(exclusive=True)
            queue_name = result.method.queue

            self.channel.queue_bind(exchange=current_exchange_name, queue=queue_name)
            self.channel.basic_consume(self._callback, queue=queue_name, no_ack=True)

            # prepare tasks queues (not broadcast)
            current_exchange_name = self.EXCHANGE_PREFIX_SINGLE + event_name
            self.channel.exchange_declare(
                exchange=current_exchange_name,
                type="direct"
            )
            self.channel.queue_declare(queue=event_name)
            queue_name = event_name
            self.channel.queue_bind(exchange=current_exchange_name, queue=queue_name,
                                    routing_key='tasks')
            self.channel.basic_consume(self._callback, queue=queue_name)

        self.channel.start_consuming()

    def _callback(self, channel, method, properties, body):
        if not method.exchange.startswith(self.EXCHANGE_PREFIX_BROADCAST) or \
                not method.exchange.startswith(self.EXCHANGE_PREFIX_SINGLE):
            return

        if method.exchange.startswith(self.EXCHANGE_PREFIX_SINGLE):
            event_name = method.exchange[len(self.EXCHANGE_PREFIX_SINGLE):]
            try:
                self.on_event_received(event_name, body)
            except Exception:
                self.channel.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
            else:
                self.channel.basic_ack(delivery_tag=method.delivery_tag)

        event_name = method.exchange[len(self.EXCHANGE_PREFIX_BROADCAST):]
        self.on_event_received(event_name, body)

    def on_event_received(self, event_name, event_body):
        handler = self._handlers.get(event_name)
        if not handler:
            return
        if isinstance(event_body, bytes):
            event_body = event_body.decode()

        handler(json.loads(event_body))

    def emit_event(self, event_name, event_body, *, broadcast=True):
        exchange_name = (self.EXCHANGE_PREFIX_BROADCAST
                         if broadcast else self.EXCHANGE_PREFIX_SINGLE) + event_name

        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key='' if broadcast else "tasks",
            body=json.dumps(event_body)
        )

    def __del__(self):
        if hasattr(self, "channel"):
            self.channel.close()
