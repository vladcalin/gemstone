from gemstone import MicroService, event_handler, exposed_method
from gemstone.event.transport import rabbitmq, redis_transport


class EventTestService2(MicroService):
    name = "event.test2"
    host = "127.0.0.1"
    port = 8000

    event_transports = [
        redis_transport.RedisEventTransport("redis://127.0.0.1:6379/0")
    ]

    @exposed_method()
    def say_hello(self, name):
        self.emit_event("said_hello", {"name": name})
        return "Hello {}".format(name)


if __name__ == '__main__':
    service = EventTestService2()
    service.start()
