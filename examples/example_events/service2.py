from gemstone import MicroService, event_handler, public_method
from gemstone.event.transport import rabbitmq


class EventTestService2(MicroService):
    name = "event.test2"
    host = "127.0.0.1"
    port = 8000

    event_transports = [
        rabbitmq.RabbitMqEventTransport(host="192.168.1.71", username="admin", password="X5f6rPmx1yYz")
    ]

    @public_method
    def say_hello(self, name):
        self.emit_event("said_hello", {"name": name})
        return "Hello {}".format(name)


if __name__ == '__main__':
    cli = EventTestService2.get_cli()
    cli()
