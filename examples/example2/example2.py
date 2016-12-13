import os

from tornado.web import RequestHandler
from tornado.gen import coroutine

from pymicroservice.core.microservice import PyMicroService
from pymicroservice.core.decorators import public_method, private_api_method


def print_stuff():
    print("hello there")


class ExampleService2(PyMicroService):
    name = "service.hellworld"
    host = "127.0.0.1"
    port = 10000

    api_token_header = "X-Api-Token"
    max_parallel_blocking_tasks = os.cpu_count()
#    periodic_tasks = [(print_stuff, 1)]

    service_registry_urls = [
        "http://localhost:8000/api"
    ]

    @public_method
    def say_hello(self, name):
        return "hello {}".format(name)

    @public_method
    def remote(self, name):
        service3 = self.get_service("service.3")
        resp = service3.methods.say_hello(name)
        return "Service 3 said {}".format(resp)



if __name__ == '__main__':
    service = ExampleService2()
    service.start()
