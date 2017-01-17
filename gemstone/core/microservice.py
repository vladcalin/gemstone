import logging
from abc import ABC, abstractmethod
import os
from concurrent.futures import ThreadPoolExecutor
import functools
import random
import argparse

from tornado.web import RequestHandler, StaticFileHandler
from tornado.gen import coroutine
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import Application
from tornado.log import enable_pretty_logging

from gemstone.errors import ServiceConfigurationError, AccessDeniedError
from gemstone.core.handlers import TornadoJsonRpcHandler
from gemstone.core.decorators import public_method
from gemstone.client.remote_service import RemoteService

__all__ = [
    'MicroService'
]


class MicroService(ABC):
    name = None

    host = "127.0.0.1"
    port = 8000
    accessible_at = None

    # extra Tornado configuration
    template_dir = "."
    static_dirs = []
    extra_handlers = []

    # protocol specs
    api_token_header = "X-Api-Token"

    # service registry integration
    service_registry_urls = []
    service_registry_ping_interval = 30

    # periodic tasks
    periodic_tasks = []
    default_periodic_tasks = []

    # io event related
    max_parallel_blocking_tasks = os.cpu_count()
    _executor = None

    def __init__(self, io_loop=None):
        """

        The base class for implementing microservices.

        :param io_loop: A :py:class:`tornado.ioloop.IOLoop` instance -
                        can be used to share the same io loop between
                        multiple microservices running from the same process.
        """
        self.app = None
        self._periodic_tasks_objs = []
        self.logger = self.get_logger()
        self.registries = []

        # name
        if self.name is None:
            raise ServiceConfigurationError("No name defined for the microservice")

        # methods
        self.methods = {}
        self.gather_exposed_methods()

        if len(self.methods) == 0:
            raise ServiceConfigurationError("No exposed methods for the microservice")

        # executor
        if self.max_parallel_blocking_tasks <= 0:
            raise ServiceConfigurationError("Invalid max_parallel_blocking_tasks value")

        self._executor = ThreadPoolExecutor(self.max_parallel_blocking_tasks)

        # ioloop
        self.io_loop = io_loop or IOLoop.current()

    @public_method
    def get_service_specs(self):
        """
        A default exposed method that returns the current microservice specifications. The returned information is
        in the format:

        ::

            {
                "host": "127.0.0.1",
                "port": 9000,
                "name": "service.example",
                "max_parallel_blocking_tasks": 8,
                "methods": {
                    "get_service_specs": "...",
                    "method1": "method1's docstring",
                    ...
                }
            }

        :return:
        """
        return {
            "host": self.host,
            "port": self.port,
            "accessible_at": self.accessible_at or "http://{}:{}/api".format(self.host, self.port),
            "name": self.name,
            "max_parallel_blocking_tasks": self.max_parallel_blocking_tasks,
            "methods": {m: self.methods[m].__doc__ for m in self.methods}
        }

    def on_service_start(self):
        """
        Override this method to do a set of actions when the service starts

        :return: ``None``
        """
        pass

    def start(self):
        """
        The main method that starts the service. This is blocking.

        """
        self.on_service_start()
        self.app = self.make_tornado_app()
        enable_pretty_logging()
        self.app.listen(self.port, address=self.host)

        for periodic_task in self.periodic_task_iter():
            self.logger.debug("Starting periodic task {}".format(periodic_task))
            periodic_task.start()

        try:
            self.io_loop.start()
        except RuntimeError:
            pass

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
        :return: ``True`` if the api_token is valid, ``False`` otherwise
        """
        return True

    def gather_exposed_methods(self):
        for itemname in dir(self):
            item = getattr(self, itemname)
            if getattr(item, "__is_exposed_method__", False) is True or \
                            getattr(item, "__private_api_method__", False) is True:
                self.methods[item.__name__] = item

    def get_logger(self):
        """
        Override this method to designate the logger for the application

        :return: a :py:class:`logging.Logger` instance
        """
        return logging.getLogger("tornado.application")

    def ping_to_service_registry(self, servreg_remote_service):
        host, port = self.accessible_at or (self.host, self.port)
        servreg_remote_service.notifications.ping(name=self.name, host=host, port=port)

    def periodic_task_iter(self):
        for url in self.service_registry_urls:
            registry = RemoteService(url)
            self.registries.append(registry)
            periodic_servreg_ping = functools.partial(self.ping_to_service_registry, registry)
            periodic_servreg_ping()  # initial ping
            self.default_periodic_tasks.append(
                (periodic_servreg_ping, self.service_registry_ping_interval)
            )

        all_periodic_tasks = self.default_periodic_tasks + self.periodic_tasks
        for func, timer_in_seconds in all_periodic_tasks:
            timer_milisec = timer_in_seconds * 1000
            yield PeriodicCallback(func, timer_milisec, io_loop=self.io_loop)

    def get_service(self, name):
        """
        Locates a remote service by name. The name can be a glob-like pattern (``"project.worker.*"``). If multiple
        services match the given name, a random instance will be chosen. There might be multiple services that match
        a given name if there are multiple services with the same name running, or when the pattern matches
        multiple different services.

        .. todo::

            Make this use self.io_loop to resolve the request. The current implementation is blocking and slow

        :param name: a pattern for the searched service.
        :return: a :py:class:`gemstone.RemoteService` instance
        :raises ValueError: when the service can not be located
        :raises ServiceConfigurationError: when there is no configured service registry
        """
        if not self.registries:
            raise ServiceConfigurationError("No service registry available")

        for service_reg in self.registries:
            services = service_reg.methods.locate_service(name)
            if not services:
                continue
            random.shuffle(services)
            for service in services:
                url = "http://" + service["host"] + ":" + str(service["port"]) + "/api"
                try:
                    return RemoteService(url)
                except ConnectionError:
                    continue  # could not establish connection, try next

        raise ValueError("Service could not be located")

    @classmethod
    def get_cli(cls):
        """
        Creates a command line interface through which the user
        can override specific options of the microservice. Useful when
        the user might want to dynamically change the configuration
        of the microservice.

        For example, having another script that dynamically starts instances
        of our microservice that each listen to different ports.

        The returned value is a function than when called, parses the arguments,
        overrides the defaults and then starts the microservice.

        Example usage

        .. code-block:: python

            # in service.py

            cli = MyMicroService.get_cli()
            cli()

        After that, from the command line, we can do the following

        .. code-block:: bash

            python service.py --help    # show the help
            python service.py start     # start the microservice with the default parameters
            python service.py start --help  # show the configurable parameters
            python service.py start --port=8000 --host=0.0.0.0 --service_registry http://127.0.0.1/api http://192.168.0.11/api  # override some parameters


        :return: a function that can override and start the microservice, depending on the command line arguments

        .. versionadded:: 0.1.0
        """
        parser = argparse.ArgumentParser()

        subparser = parser.add_subparsers()

        # myservice.py start [--opt=val]*
        start_parser = subparser.add_parser("start")
        start_parser.add_argument("--name", help="The name of the microservice. Currently {}".format(cls.name))
        start_parser.add_argument("--host", help="The address to bind to. Currently {}".format(cls.host))
        start_parser.add_argument("--port", help="The port to bind to. Currently {}".format(cls.port), type=int)
        start_parser.add_argument("--api_token_header", help="The header to be used for access validation."
                                                             "Currently {}".format(cls.api_token_header))
        start_parser.add_argument("--max_parallel_tasks", help="Maximum number of methods to be"
                                                               "executed concurrently. Currently {}".format(
                                                                cls.max_parallel_blocking_tasks))
        start_parser.add_argument("--service_registry", nargs="*",
                                  help="A url where a service registry can be found. Currently {}".format(
                                      cls.service_registry_urls))

        def start():
            cls().start()

        start_parser.set_defaults(func=start)

        def call_argument_parser():
            args = parser.parse_args()

            cls._set_option_if_available(args, "name")
            cls._set_option_if_available(args, "host")
            cls._set_option_if_available(args, "port")
            cls._set_option_if_available(args, "api_token_header")
            cls._set_option_if_available(args, "max_parallel_tasks")
            if getattr(args, "service_registry", None):
                cls.service_registry_urls = args.service_registry

            args.func()

        return call_argument_parser

    @classmethod
    def _set_option_if_available(cls, args, name):
        if hasattr(args, name) and getattr(args, name) is not None:
            setattr(cls, name, getattr(args, name))
