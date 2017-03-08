import gemstone

from gemstone.event.transport import RabbitMqEventTransport


class ProducerService(gemstone.MicroService):
    name = "producer"
    port = 8000

    event_transports = [
        RabbitMqEventTransport("192.168.1.71", 5672, username="admin", password="X5f6rPmx1yYz")
    ]

    @gemstone.exposed_method()
    def broadcast_msg(self, message):
        self.emit_event("test", {"msg": message}, broadcast=True)
        return True

    @gemstone.exposed_method()
    def single_msg(self, message):
        self.emit_event("test", {"msg": message}, broadcast=False)
        return True


if __name__ == '__main__':
    ProducerService().start()
