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
    def test1(self):
        return "test1_ok"

    @public_method
    def test2(self, arg1, arg2):
        return arg1 + arg2

    @private_api_method
    def test3(self, msg):
        return {
            "response": msg
        }

    @public_method
    def test_raises(self):
        raise ValueError("This is a test")

    def api_token_is_valid(self, api_token):
        return api_token == "testing_token"


class TestServiceWithCookieAuth(MicroService):
    name = "service.test.3"
    host = TEST_HOST
    port = TEST_PORT + 1

    validation_strategies = [
        BasicCookieStrategy(cookie_name="AuthToken")
    ]

    @private_api_method
    def test(self, arg):
        return arg

    def api_token_is_valid(self, api_token):
        return api_token == "test_ok"
