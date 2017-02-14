import logging
import os
import functools
import random
import argparse
import threading
import sys
from abc import ABC
from concurrent.futures import ThreadPoolExecutor

from tornado.web import StaticFileHandler
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import Application
from tornado.log import enable_pretty_logging

from gemstone.config.configurable import Configurable
from gemstone.config.configurator import CommandLineConfigurator
from gemstone.errors import ServiceConfigurationError
from gemstone.core.handlers import TornadoJsonRpcHandler
from gemstone.core.decorators import public_method
from gemstone.client.remote_service import RemoteService
from gemstone.auth.validation_strategies.header_strategy import HeaderValidationStrategy

__all__ = [
    'MicroService'
]

IS_WINDOWS = sys.platform.startswith("win32")


class MicroService(ABC):
    # service metadata
    name = None

    # accessibility
    host = "127.0.0.1"
    port = 8000
    accessible_at = None
    endpoint = "/api"

    # webapp configuration
    template_dir = "."
    static_dirs = []
    extra_handlers = []

    # access control
    validation_strategies = [
        HeaderValidationStrategy(header_name="X-Api-Token")
    ]

    # auto-discovery
    service_registry_urls = []
    service_registry_ping_interval = 30

    # periodic tasks
    periodic_tasks = []

    # event handlers
    event_transports = []

    # configurable framework
    skip_configuration = False
    configurables = [
        Configurable("port", type=int, mappings={"random": lambda _: random.randint(8000, 65000)}),
        Configurable("host"),
        Configurable("accessible_at"),
        Configurable("endpoint"),
        Configurable("service_registry_urls", template=lambda s: s.split(","))
    ]
    configurators = [
        CommandLineConfigurator()
    ]

    # in some situations, on Windows the event loop may hang
    # http://stackoverflow.com/questions/33634956/why-would-a-timeout-avoid-a-tornado-hang/33643631#33643631
    default_periodic_tasks = [(lambda: None, 0.5)] if IS_WINDOWS else []

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

        self.logger.info("Initializing")

        # name
        if self.name is None:
            raise ServiceConfigurationError("No name defined for the microservice")
        self.logger.debug("Service name: {}".format(self.name))

        # endpoint
        if self.accessible_at is None:
            self.accessible_at = "http://{host}:{port}{endpoint}".format(
                host=self.host, port=self.port, endpoint=self.endpoint
            )

        # methods
        self.methods = {}
        self._gather_exposed_methods()

        # event handlers
        self.event_handlers = {}
        self._gather_event_handlers()

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
            "accessible_at": self.accessible_at,
            "name": self.name,
            "max_parallel_blocking_tasks": self.max_parallel_blocking_tasks,
            "methods": {m: self.methods[m].__doc__ for m in self.methods},
            "event_transports": [str(t) for t in self.event_transports],
            "events_handled": {ev_name: ev_handle.__doc__ for ev_name, ev_handle in self.event_handlers.items()}
        }

    # region Can be overridden by user

    def on_service_start(self):
        """
        Override this method to do a set of actions when the service starts

        :return: ``None``
        """
        pass

    def api_token_is_valid(self, api_token):
        """
        Method that must be overridden by subclasses in order to implement the API token validation logic.
        Should return ``True`` if the api token is valid, or ``False`` otherwise.

        :param api_token: a string representing the received api token value
        :return: ``True`` if the api_token is valid, ``False`` otherwise
        """
        return True

    def get_logger(self):
        """
        Override this method to designate the logger for the application

        :return: a :py:class:`logging.Logger` instance
        """
        enable_pretty_logging()
        return logging.getLogger("tornado.application")

    # endregion

    # region Can be called by user

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
            endpoints = service_reg.methods.locate_service(name)
            if not endpoints:
                continue
            random.shuffle(endpoints)
            for url in endpoints:
                try:
                    return RemoteService(url)
                except ConnectionError:
                    continue  # could not establish connection, try next

        raise ValueError("Service could not be located")

    def start_thread(self, target, args, kwargs):
        """
        Shortcut method for starting a thread.

        :param target: The function to be executed.
        :param args: A tuple or list representing the positional arguments for the thread.
        :param kwargs: A dictionary representing the keyword arguments.

        .. versionadded:: 0.5.0
        """
        thread_obj = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
        thread_obj.start()

    def emit_event(self, event_name, event_body):
        """
        Publishes an event of type ``event_name`` to all subscribers, having the body ``event_body``. The event
        is pushed through all available event transports.

        The event body must be a Python object that can be represented as a JSON.

        :param event_name: a ``str`` representing the event type
        :param event_body: a Python object that can be represented as JSON.

        .. versionadded:: 0.5.0
        """

        for transport in self.event_transports:
            transport.emit_event(event_name, event_body)

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


        :return: a function that can override parameters and start the microservice, depending on the command line arguments

        .. versionadded:: 0.1.0
        """
        parser = argparse.ArgumentParser()

        subparser = parser.add_subparsers()

        # myservice.py start [--opt=val]*
        start_parser = subparser.add_parser("start")
        start_parser.add_argument("--name", help="The name of the microservice. Currently {}".format(cls.name))
        start_parser.add_argument("--host", help="The address to bind to. Currently {}".format(cls.host))
        start_parser.add_argument("--port", help="The port to bind to. Currently {}".format(cls.port), type=int)
        start_parser.add_argument("--accessible_at", help="The URL where the service can be accessed")
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
            cls._set_option_if_available(args, "max_parallel_tasks")
            cls._set_option_if_available(args, "accessible_at")
            if getattr(args, "service_registry", None):
                cls.service_registry_urls = args.service_registry

            if hasattr(args, "func"):
                args.func()
            else:
                parser.print_help()

        return call_argument_parser

    def start(self):
        """
        The main method that starts the service. This is blocking.

        """
        self._before_start_setup()
        self.on_service_start()
        self.app = self.make_tornado_app()
        enable_pretty_logging()
        self.app.listen(self.port, address=self.host)

        for k, v in self.get_current_configuration().items():
            self.logger.debug("{}={}".format(k, v))

        for periodic_task in self._periodic_task_iter():
            self.logger.debug("Starting periodic task {}".format(periodic_task))
            periodic_task.start()

        # starts the event handlers
        self._initialize_event_handlers()
        self._start_event_handlers()

        try:
            self.io_loop.start()
        except RuntimeError:
            # TODO : find a way to check if the io_loop is running before trying to start it
            # this method to check if the loop is running is ugly
            pass

    def get_current_configuration(self):
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "endpoint": self.endpoint,
            "accessible_at": self.accessible_at,
            "autodiscovery": {
                "service_registry_urls": self.service_registry_urls,
                "service_registry_ping_interval": self.service_registry_ping_interval,
            },
            "max_parallel_blocking_tasks": self.max_parallel_blocking_tasks,
            "webapp": {
                "template_dir": self.template_dir,
                "static_dirs": self.static_dirs,
                "extra_handlers": [str(h) for h in self.extra_handlers]
            },
            "access_control": {
                "validation_strategies": [str(v) for v in self.validation_strategies]
            },
            "event": {
                "event_transports": [str(t) for t in self.event_transports]
            },
            "configuration": {
                "configurables": [str(c) for c in self.configurables],
                "configurators": [str(c) for c in self.configurators]
            }

        }

    # endregion

    def _before_start_setup(self):
        if not self.skip_configuration:
            self._prepare_configurators()
            self._activate_configurators()

    def _initialize_event_handlers(self):
        for event_transport in self.event_transports:
            self.logger.debug("Initializing transport {}".format(event_transport))
            for event_name, event_handler in self.event_handlers.items():
                self.logger.debug("Setting handler for {}".format(event_name))
                event_transport.register_event_handler(event_handler, event_name)

    def _start_event_handlers(self):
        for event_transport in self.event_transports:
            self.start_thread(
                target=event_transport.start_accepting_events, args=(), kwargs={}
            )

    def make_tornado_app(self):
        """
        Creates a :py:class`tornado.web.Application` instance that respect the JSON RPC 2.0 specs and
        exposes the designated methods.

        :return: a :py:class:`tornado.web.Application` instance
        """

        handlers = [
            (self.endpoint, TornadoJsonRpcHandler,
             {
                 "logger": self.logger,
                 "methods": self.methods,
                 "executor": self._executor,
                 "validation_strategies":
                     self.validation_strategies,
                 "api_token_handler": self.api_token_is_valid
             })
        ]

        self._add_extra_handlers(handlers)
        self._add_static_handlers(handlers)

        return Application(handlers, template_path=self.template_dir)

    def _add_extra_handlers(self, handlers):
        """
        Adds the extra handler (defined by the user)

        :param handlers: a list of :py:class:`tornado.web.RequestHandler` instances.
        :return:
        """
        handlers.extend(self.extra_handlers)

    def _add_static_handlers(self, handlers):
        """
        Creates and adds the handles needed for serving static files.

        :param handlers:
        """
        for url, path in self.static_dirs:
            handlers.append((url.rstrip("/") + "/(.*)", StaticFileHandler, {"path": path}))

    def _gather_exposed_methods(self):
        """
        Searches for the exposed methods in the current microservice class. A method is considered
        exposed if it is decorated with the :py:func:`gemstone.public_method` or
        :py:func:`gemstone.private_api_method`.
        """

        for itemname in dir(self):
            item = getattr(self, itemname)
            if getattr(item, "__is_exposed_method__", False) is True or \
                            getattr(item, "__private_api_method__", False) is True:
                self.methods[item.__name__] = item

    def _gather_event_handlers(self):
        """
        Searches for the event handlers in the current microservice class.

        :return:
        """
        for itemname in dir(self):
            item = getattr(self, itemname)
            if getattr(item, "__is_event_handler__", False):
                self.event_handlers.setdefault(item.__handled_event__, item)

    def _ping_to_service_registry(self, servreg_remote_service):
        """
        Notifies a service registry about the service (its name and http location)

        :param servreg_remote_service: a :py:class:`gemstone.RemoteService` instance
        """
        url = self.accessible_at
        self.logger.debug("Pinging {registry_url} (name={name}, url={url})".format(
            registry_url=servreg_remote_service.url, name=self.name, url=url
        ))
        servreg_remote_service.notifications.ping(name=self.name, url=url)

    def _periodic_task_iter(self):
        """
        Iterates through all the periodic tasks:

        - the service registry pinging
        - default dummy task if on Windows
        - user defined periodic tasks

        :return:
        """
        for url in self.service_registry_urls:
            registry = RemoteService(url)
            self.registries.append(registry)
            periodic_servreg_ping = functools.partial(self._ping_to_service_registry, registry)
            periodic_servreg_ping()  # initial ping
            self.default_periodic_tasks.append(
                (periodic_servreg_ping, self.service_registry_ping_interval)
            )

        all_periodic_tasks = self.default_periodic_tasks + self.periodic_tasks
        for func, timer_in_seconds in all_periodic_tasks:
            timer_milisec = timer_in_seconds * 1000
            yield PeriodicCallback(func, timer_milisec, io_loop=self.io_loop)

    @classmethod
    def _set_option_if_available(cls, args, name):
        if hasattr(args, name) and getattr(args, name) is not None:
            setattr(cls, name, getattr(args, name))

    def _prepare_configurators(self):
        for configurator in self.configurators:
            for configurable in self.configurables:
                configurator.register_configurable(configurable)

    def _activate_configurators(self):
        for configurator in self.configurators:
            configurator.load()

        for configurator in self.configurators:
            for configurable in self.configurables:
                name = configurable.name
                value = configurator.get(name)
                if not value:
                    continue

                setattr(self, name, value)
