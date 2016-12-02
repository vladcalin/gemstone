import inspect
from abc import ABC, abstractmethod
import os
from concurrent.futures import ThreadPoolExecutor
import functools

from tornado.web import RequestHandler, StaticFileHandler
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.log import enable_pretty_logging

from pymicroservice.util import init_default_logger
from pymicroservice.errors import ServiceConfigurationError, AccessDeniedError
from pymicroservice.core.handlers import TornadoJsonRpcHandler
from pymicroservice.core.decorators import public_method

__all__ = [
    'PyMicroService'
]


class PyMicroService(ABC):
    """

    The base class for defining a microservice.
    A microservice must define:

    Service parameters that can be defined:

    - [Required] ``name`` : a string representing an identifier of the service
    - ``host`` : a string representing an address to bind to (defaults to 127.0.0.1)
    - ``port`` : an integer representing the port to which to bind
    - ``api_token_header`` : the HTTP header to be used for authorized API access
    - ``max_parallel_blocking_tasks`` :the maximum number of blocking tasks that can be executed at
        the same moment (using a :py:class:`concurrent.futures.ThreadPoolExecutor` instance). Defaults
        to :py:func:`os.cpu_count`.

    """
    name = None

    host = "127.0.0.1"
    port = 8000

    template_dir = "."
    static_dirs = []
    extra_handlers = []

    api_token_header = "X-Api-Token"

    max_parallel_blocking_tasks = os.cpu_count()
    _executor = None

    methods = {}
    private_methods = {}

    def __init__(self):
        self.app = None
        init_default_logger()

        # name
        if self.name is None:
            raise ServiceConfigurationError("No name defined for the microservice")

        # methods
        self.gather_exposed_methods()

        if len(self.methods) == 0:
            raise ServiceConfigurationError("No exposed methods for the microservice")

        # executor
        if self.max_parallel_blocking_tasks <= 0:
            raise ServiceConfigurationError("Invalid max_parallel_blocking_tasks value")

        self._executor = ThreadPoolExecutor(self.max_parallel_blocking_tasks)

    @public_method
    def get_service_specs(self):
        return {
            "host": self.host,
            "port": self.port,
            "name": self.name,
            "max_parallel_blocking_tasks": self.max_parallel_blocking_tasks,
            "methods": {m: self.methods[m].__doc__ for m in self.methods}
        }

    def start(self):
        """
        The main method that starts the service. This is blocking.

        """
        self.app = self.make_tornado_app()
        enable_pretty_logging()
        self.app.listen(self.port, address=self.host)
        IOLoop.current().start()

    def make_tornado_app(self):

        handlers = [
            (r"/api", TornadoJsonRpcHandler,
             {
                 "methods": self.methods,
                 "executor": self._executor,
                 "api_token_header":
                     self.api_token_header,
                 "api_token_handler": self.api_token_is_valid
             })
        ]

        self.add_extra_handlers(handlers)
        self.add_static_handlers(handlers)

        return Application(handlers, template_path=self.template_dir)

    def add_extra_handlers(self, handlers):
        handlers.extend(self.extra_handlers)

    def add_static_handlers(self, handlers):
        for url, path in self.static_dirs:
            handlers.append((url.rstrip("/") + "/(.*)", StaticFileHandler, {"path": path}))

    def api_token_is_valid(self, api_token):
        """
        Method that must be overridden by subclasses in order to implement the API token validation logic.
        Should return ``True`` if the api token is valid, or ``False`` otherwise.

        :param api_token: a string representing the received api token value
        :return:
        """
        return True

    def gather_exposed_methods(self):
        for itemname in dir(self):
            item = getattr(self, itemname)
            if getattr(item, "__is_exposed_method__", False) is True or \
                            getattr(item, "__private_api_method__", False) is True:
                self.methods[item.__name__] = item
