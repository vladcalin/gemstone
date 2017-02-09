from gemstone import MicroService, event_handler
from gemstone.event.transport import rabbitmq


class EventTestService(MicroService):
    name = "event.test"
    host = "127.0.0.1"
    port = 8080

    event_transports = [
        rabbitmq.RabbitMqEventTransport(host="192.168.1.71", username="admin", password="X5f6rPmx1yYz")
    ]

    @event_handler("said_hello")
    def event_one_handler(self, body):
        self.logger.warning(body)
        self.logger.info("Somewhere, {} said hello :)".format(body["name"]))


if __name__ == '__main__':
    cli = EventTestService.get_cli()
    cli()
