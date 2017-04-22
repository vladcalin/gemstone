from gemstone.core import MicroService, exposed_method


class ServiceJsonRpcSpecs(MicroService):
    name = "test.service"

    host = "127.0.0.1"
    port = 9999

    skip_configuration = True

    @exposed_method()
    def subtract(self, a, b):
        if not isinstance(a, int) or not isinstance(b, int):
            raise TypeError("Arguments must be integers")
        return a - b

    @exposed_method()
    def sum(self, *args):
        return sum(args)

    @exposed_method()
    def update(self, a):
        return str(a)

    @exposed_method()
    def get_data(self):
        return ["hello", 5]

    @exposed_method()
    def notify_hello(self, a):
        return a


if __name__ == '__main__':
    service = ServiceJsonRpcSpecs()
    service.start()
