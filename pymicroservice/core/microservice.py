import inspect
from abc import ABC, abstractmethod
import os
from concurrent.futures import ThreadPoolExecutor

from tornado.web import RequestHandler
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.log import enable_pretty_logging

from pymicroservice.util import init_default_logger
from pymicroservice.errors import ServiceConfigurationError
from pymicroservice.core.handlers import TornadoJsonRpcHandler
from pymicroservice.core.decorators import exposed_method

__all__ = [
    'TornadoJsonRpcHandler'
]


class PyMicroService(ABC):
    """

    The base class for fast building a microservice. The microservice must:

    - define a name attribute for easy identification (must be a string)
    - max_parallel_blocking_tasks must be a positive integer
    - a bunch of exposed methods decorated with the :py:class:`pymicroservice.exposed_method` decorator

    The default implementation spawns a Tornado JSON RPC HTTP server.

    The service exposes the default rpc function **get_service_specs** which returns the running parameters of
    the service.

    """
    name = None

    host = "127.0.0.1"
    port = 8000

    max_parallel_blocking_tasks = os.cpu_count()
    _executor = None

    methods = {}

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

    @exposed_method
    def get_service_specs(self):
        return {
            "host": self.host,
            "port": self.port,
            "name": self.name,
            "max_parallel_blocking_tasks": self.max_parallel_blocking_tasks
        }

    def start(self):
        self.app = self.make_tornado_app()
        enable_pretty_logging()
        self.app.listen(self.port, address=self.host)
        IOLoop.current().start()

    def make_tornado_app(self):
        return Application([
            (r"/api", TornadoJsonRpcHandler, {"methods": self.methods, "executor": self._executor})
        ])

    def gather_exposed_methods(self):
        for itemname in dir(self):
            item = getattr(self, itemname)
            if getattr(item, "__is_exposed_method__", False) is True:
                self.methods[item.__name__] = item
