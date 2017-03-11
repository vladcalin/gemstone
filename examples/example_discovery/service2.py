import gemstone
from gemstone.discovery.default import DefaultDiscoveryStrategy


class Service2(gemstone.MicroService):
    name = "service.2"

    port = 9000

    discovery_strategies = [
        DefaultDiscoveryStrategy("http://localhost:8080/api")
    ]

    @gemstone.exposed_method()
    def say_hello(self, name):
        return "hello {}".format(name)


if __name__ == '__main__':
    Service2().start()
