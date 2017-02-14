import time
from gemstone.auth.validation_strategies.header_strategy import HeaderValidationStrategy

from gemstone import MicroService, public_method, private_api_method

HOST, PORT = "127.0.0.1", 6799
PORT2 = PORT + 1


class Service1(MicroService):
    name = "test.service.client.1"
    skip_configuration = True

    host = HOST
    port = PORT

    @public_method
    def method1(self):
        return "hello there"

    @public_method
    def method2(self, arg):
        return "hello there {}".format(arg)

    @public_method
    def method3(self, a, b):
        if not isinstance(a, int) or not isinstance(b, int):
            raise ValueError("Bad type for a and b")
        return a + b

    @public_method
    def sleep(self, seconds):
        time.sleep(seconds)
        return seconds

    @public_method
    def sleep_with_error(self, seconds):
        time.sleep(seconds)
        raise ValueError(seconds)

    @public_method
    def method4(self, arg1, arg2):
        return {"arg1": arg1, "arg2": arg2}

    @private_api_method
    def method5(self, name):
        return "private {}".format(name)

    def api_token_is_valid(self, api_token):
        return api_token == "test-token"


class Service2(MicroService):
    name = "test.service.client.2"
    skip_configuration = True

    validation_strategies = [
        HeaderValidationStrategy(header_name="Custom-Header")
    ]

    host = HOST
    port = PORT2

    @private_api_method
    def test(self):
        return True

    def api_token_is_valid(self, api_token):
        return api_token == "test-token"
