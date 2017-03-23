import gemstone
from gemstone.discovery.default import DefaultDiscoveryStrategy
from gemstone.discovery.redis_strategy import RedisDiscoveryStrategy


class Service2(gemstone.MicroService):
    name = "service.2"

    port = 9000

    discovery_strategies = [
        RedisDiscoveryStrategy("redis://localhost:6379/0")
    ]

    @gemstone.exposed_method()
    def say_hello(self, name):
        return "hello {}".format(name)


if __name__ == '__main__':
    Service2().start()
