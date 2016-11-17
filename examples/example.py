from pymicroservice.core.microservice import PyMicroService
from pymicroservice.core.decorators import endpoint, async_endpoint


class HelloWorldService(PyMicroService):
    name = "hello.world.service"

    def __init__(self):
        super(HelloWorldService, self).__init__()
        self._values = {}

    @endpoint
    def say_hello(self, name):
        return "hello {}".format(name)

    @endpoint
    def store_value(self, name, value):
        self._values[name] = value
        return "ok"

    @endpoint
    def retrieve_value(self, name):
        return self._values[name]


if __name__ == '__main__':
    service = HelloWorldService()
    service.start()
