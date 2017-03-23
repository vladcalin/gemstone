import random
import time
import gemstone

from tornado.gen import sleep


class TestMicroservice(gemstone.MicroService):
    name = "test"
    host = "127.0.0.1"
    port = 8000
    endpoint = "/api"

    @gemstone.exposed_method()
    def say_hello(self, name):
        return "hello {}".format(name)

    @gemstone.exposed_method(is_coroutine=True)
    def slow_method(self, seconds):
        yield sleep(seconds)
        return "finished sleeping for {} seconds".format(seconds)


if __name__ == '__main__':
    service = TestMicroservice()
    service.start()
