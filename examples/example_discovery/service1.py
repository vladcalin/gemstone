import gemstone
from gemstone.discovery.default import DefaultDiscoveryStrategy
from gemstone.discovery.redis_strategy import RedisDiscoveryStrategy


class Service1(gemstone.MicroService):
    name = "service.1"

    port = 8000

    discovery_strategies = [
        RedisDiscoveryStrategy("redis://localhost:6379/0")
    ]

    @gemstone.exposed_method()
    def say_hello(self, name):
        remote_service = self.get_service("service.2")
        print(remote_service)
        result = remote_service.call_method("say_hello", params=[name])
        return result.result


if __name__ == '__main__':
    Service1().start()
