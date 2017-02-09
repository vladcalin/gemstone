import os

from tornado.web import RequestHandler
from tornado.gen import coroutine

from gemstone.core.microservice import MicroService
from gemstone.core.decorators import public_method, private_api_method


class IndexHandler(RequestHandler):
    @coroutine
    def get(self):
        self.render("index.html")


class HelloWorldService(MicroService):
    name = "hello.world.service"
    host = "127.0.0.1"
    port = 5000

    accessible_at = "http://localhost:5000/api"

    service_registry_urls = []

    extra_handlers = [
        (r"/app", IndexHandler),
    ]
    template_dir = "templates"

    static_dirs = [
        (r"/static", "static"),
    ]

    def __init__(self):
        self._values = {}
        super(HelloWorldService, self).__init__()

    @public_method
    def say_hello(self, name):
        return "hello {}".format(name)

    @public_method
    def store_value(self, name, value):
        """
        Stores the value internally.
        """
        self._values[name] = value
        return "ok"

    @private_api_method
    def retrieve_value(self, name):
        """
        Retrieves a value that was previously stored.
        """
        return self._values[name]

    @public_method
    def more_stuff(self, x, y, k=3, *args, **kwargs):
        return "ok"

    def api_token_is_valid(self, api_token):
        return api_token == "test"


if __name__ == '__main__':
    cli = HelloWorldService.get_cli()
    cli()
