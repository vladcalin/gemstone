from pymicroservice.core.microservice import BaseMicroService
from pymicroservice.core.decorators import endpoint
from pymicroservice.concrete.tornado_json_rpc_service import TornadoJsonRpcService


class HelloWorldService(TornadoJsonRpcService):
    name = "hello.world.service"
    host = "127.0.0.1"
    port = 5000

    extras = [
        # RegisterWithServiceRegistryExtra(("127.0.0.1", 8000))
    ]

    def __init__(self):
        self._values = {}
        super(HelloWorldService, self).__init__()

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
