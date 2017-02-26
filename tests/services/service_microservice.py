from gemstone import MicroService, public_method, private_api_method
from gemstone.auth.validation_strategies.header_strategy import HeaderValidationStrategy
from gemstone.auth.validation_strategies.basic_cookie_strategy import BasicCookieStrategy

TEST_HOST, TEST_PORT = ("localhost", 65503)


class TestService(MicroService):
    name = "service.test.2"

    host = TEST_HOST
    port = TEST_PORT

    validation_strategies = [
        HeaderValidationStrategy(header_name="X-Testing-Token")
    ]

    @public_method
    def say_hello(self):
        return "hello"

    @public_method
    def subtract(self, a, b):
        return a - b

    @public_method
    def sum(self, *args):
        return sum(args)

    @public_method
    def divide(self, a, b):
        return a / b

    @private_api_method
    def private_sum(self, a, b):
        return a + b

    @public_method
    def test_raises(self):
        raise ValueError("This is a test")

    def api_token_is_valid(self, api_token):
        return api_token == "testing_token"
