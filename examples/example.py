from pymicroservice.core.microservice import PyMicroService
from pymicroservice.core.decorators import public_method, private_api_method


class HelloWorldService(PyMicroService):
    name = "hello.world.service"
    host = "127.0.0.1"
    port = 5000

    def __init__(self):
        self._values = {}
        super(HelloWorldService, self).__init__()

    @public_method
    def say_hello(self, name):
        return "hello {}".format(name)

    @public_method
    def store_value(self, name, value):
        """
        Stores the value internally.
        """
        self._values[name] = value
        return "ok"

    @private_api_method
    def retrieve_value(self, name):
        """
        Retrieves a value that was previously stored.
        """
        return self._values[name]

    @public_method
    def more_stuff(self, x, y, k=3, *args, **kwargs):
        return "ok"


if __name__ == '__main__':
    service = HelloWorldService()
    service.start()
