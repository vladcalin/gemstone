import gemstone
from gemstone.config.configurable import Configurable

class HelloWorldService(gemstone.MicroService):
    name = "hello_world_service"
    host = "127.0.0.1"
    port = 8000

    configurables = [
        Configurable("a"),
        Configurable("b", type=int),
        Configurable("c", type=bool),
    ]

    @gemstone.exposed_method()
    def say_hello(self, name):
        return "hello {}".format(name)

    def on_service_start(self):
        print("a = ", self.a)
        print("b = ", self.b)
        print("c = ", self.c)

if __name__ == '__main__':
    service = HelloWorldService()
    service.start()
