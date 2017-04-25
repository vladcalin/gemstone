from gemstone.core import MicroService, exposed_method
from gemstone.config import Configuration


class Example(MicroService):
    name = "test"
    host = "127.0.0.1"
    port = 8000

    @exposed_method()
    def sum(self, a, b):
        return a + b


if __name__ == '__main__':
    service = Example()
    service.configure(Configuration({
        "host": "127.0.0.1",
        "port": Configuration.from_env("EXAMPLE_PORT", template=int)
    }))
    service.start()
