import time

from gemstone import MicroService, exposed_method

HOST, PORT = "127.0.0.1", 6799
PORT2 = PORT + 1


class Service1(MicroService):
    name = "test.service.client.1"
    skip_configuration = True

    host = HOST
    port = PORT

    @exposed_method()
    def method1(self):
        return "hello there"

    @exposed_method()
    def method2(self, arg):
        return "hello there {}".format(arg)

    @exposed_method()
    def method3(self, a, b):
        if not isinstance(a, int) or not isinstance(b, int):
            raise ValueError("Bad type for a and b")
        return a + b

    @exposed_method()
    def sleep(self, seconds):
        time.sleep(seconds)
        return seconds

    @exposed_method()
    def sleep_with_error(self, seconds):
        time.sleep(seconds)
        raise ValueError(seconds)

    @exposed_method()
    def method4(self, arg1, arg2):
        return {"arg1": arg1, "arg2": arg2}

    @exposed_method(private=True)
    def method5(self, name):
        return "private {}".format(name)

    def authenticate_request(self, handler):
        api_token = handler.request.headers.get("x-api-token")
        return api_token == "test-token"


class Service2(MicroService):
    name = "test.service.client.2"
    skip_configuration = True

    host = HOST
    port = PORT2

    @exposed_method(private=True)
    def test(self):
        return True

    def authenticate_request(self, handler):
        api_token = handler.request.headers.get("x-api-token")
        return api_token == "test-token"
