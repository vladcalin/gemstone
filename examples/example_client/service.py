import random
import time
import gemstone
from gemstone.config.configurable import Optional, Required


class TestMicroservice(gemstone.MicroService):
    name = "test"
    host = Optional("127.0.0.1")
    port = Optional("random", mapping={"random": lambda _: random.randint(8000, 65000)})
    endpoint = Optional("/test/v1/api")

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
