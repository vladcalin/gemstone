import gemstone
from gemstone.discovery.default import DefaultDiscoveryStrategy


class Service1(gemstone.MicroService):
    name = "service.1"

    port = 8000

    discovery_strategies = [
        DefaultDiscoveryStrategy("http://localhost:8080/api")
    ]

    @gemstone.exposed_method()
    def say_hello(self, name):
        remote_service = self.get_service("service.2")
        print(remote_service)
        result = remote_service.methods.say_hello(name)
        return result


if __name__ == '__main__':
    Service1().start()
