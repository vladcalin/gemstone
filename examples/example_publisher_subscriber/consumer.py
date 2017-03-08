import gemstone

from gemstone.event.transport import RabbitMqEventTransport


class ConsumerService(gemstone.MicroService):
    name = "consumer"
    port = 8000

    event_transports = [
        RabbitMqEventTransport("192.168.1.71", 5672, username="admin", password="X5f6rPmx1yYz")
    ]

    @gemstone.event_handler("test")
    def broadcast_msg(self, message):
        print(message)


if __name__ == '__main__':
    ConsumerService().start()
