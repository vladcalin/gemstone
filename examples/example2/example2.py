import os

from tornado.web import RequestHandler
from tornado.gen import coroutine

from pymicroservice.core.microservice import PyMicroService
from pymicroservice.core.decorators import public_method, private_api_method


def print_stuff():
    print("hello there")


class ExampleService2(PyMicroService):
    name = "name.your.service"
    host = "127.0.0.1"
    port = 30001

    api_token_header = "X-Api-Token"
    max_parallel_blocking_tasks = os.cpu_count()
    periodic_tasks = [(print_stuff, 1)]

    service_registry_urls = [
        "http://localhost:8000/api"
    ]

    @public_method
    def say_hello(self, name):
        return "hello {}".format(name)


if __name__ == '__main__':
    service = ExampleService2()
    service.start()
