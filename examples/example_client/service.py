import time
import gemstone


class TestMicroservice(gemstone.MicroService):
    name = "test"
    host = "127.0.0.1"
    port = 8000
    endpoint = "/test/v1/api"

    @gemstone.public_method
    def say_hello(self, name):
        return "hello {}".format(name)

    @gemstone.public_method
    def slow_method(self, seconds):
        time.sleep(seconds)
        return "finished sleeping for {} seconds".format(seconds)


if __name__ == '__main__':
    cli = TestMicroservice.get_cli()
    cli()
