from gemstone import MicroService, exposed_method

TEST_HOST, TEST_PORT = ("localhost", 65503)


class TestService(MicroService):
    name = "service.test.2"

    host = TEST_HOST
    port = TEST_PORT

    @exposed_method()
    def say_hello(self):
        return "hello"

    @exposed_method()
    def subtract(self, a, b):
        return a - b

    @exposed_method()
    def sum(self, *args):
        return sum(args)

    @exposed_method()
    def divide(self, a, b):
        return a / b

    @exposed_method(private=True)
    def private_sum(self, a, b):
        return a + b

    @exposed_method()
    def test_raises(self):
        raise ValueError("This is a test")

    def authenticate_request(self, handler):
        api_token = handler.request.headers.get("x-testing-token")
        return api_token == "testing_token"
