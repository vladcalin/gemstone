from pymicroservice.core.microservice import PyMicroService
from pymicroservice.core.decorators import endpoint
from pymicroservice.adapters.flask_adapter import FlaskJsonRpcAdapter


class HelloWorldService(PyMicroService):
    name = "hello.world.service"
    adapters = [
        FlaskJsonRpcAdapter("127.0.0.1", 8080),
        FlaskJsonRpcAdapter("127.0.0.1", 8081),
        FlaskJsonRpcAdapter("127.0.0.1", 8082),
    ]

    extras = [
        # RegisterWithServiceRegistryExtra(("127.0.0.1", 8000))
    ]

    def __init__(self):
        super(HelloWorldService, self).__init__()
        self._values = {}

    @endpoint
    def say_hello(self, name):
        return "hello {}".format(name)

    @endpoint
    def store_value(self, name, value):
        """
        Stores the value internally.
        """
        self._values[name] = value
        return "ok"

    @endpoint
    def retrieve_value(self, name):
        """
        Retrieves a value that was previously stored.
        """
        return self._values[name]

    @endpoint
    def more_stuff(self, x, y, k=3, *args, **kwargs):
        return "ok"


if __name__ == '__main__':
    service = HelloWorldService()
    service.start()
