import inspect
from abc import ABC, abstractmethod

from pymicroservice.util import init_default_logger
from pymicroservice.errors import ConfigurationError

__all__ = [
    'BaseMicroService'
]


class BaseMicroService(ABC):
    name = None
    daemons = []

    def __init__(self):
        self.endpoints = {}

        self.logger = init_default_logger()
        self.logger.info("Starting")

    def start(self):
        self.validate_state()
        self.gather_endpoints()

    def gather_endpoints(self):
        self.logger.debug("Gathering endpoints")
        for item_name in dir(self):
            if not hasattr(self, item_name):
                continue

            item = getattr(self, item_name)
            if getattr(item, "__is_endpoint__", False) is True:
                self.logger.debug("\tDiscovered endpoint {}".format(item.__name__))
                endpoint_name = item.__name__
                endpoint_func = item
                endpoint_params = inspect.getargspec(item)
                self.endpoints[endpoint_name] = {
                    "func": endpoint_func,
                    "params": endpoint_params
                }

    def validate_state(self):
        if self.name is None:
            raise ConfigurationError("Name of the microservice not set")
