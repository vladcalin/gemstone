from gemstone import MicroService, event_handler
from gemstone.event.transport import rabbitmq, redis_transport


class EventTestService(MicroService):
    name = "event.test"
    host = "127.0.0.1"
    port = 8080

    event_transports = [
        redis_transport.RedisEventTransport("redis://127.0.0.1:6379/0")
    ]

    @event_handler("said_hello")
    def event_one_handler(self, body):
        self.logger.warning(body)
        self.logger.info("Somewhere, {} said hello :)".format(body["name"]))


if __name__ == '__main__':
    service = EventTestService()
    service.start()
