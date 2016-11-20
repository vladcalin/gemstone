from abc import ABC, abstractmethod

from multiprocessing.pool import ThreadPool
from pymicroservice.util import init_default_logger
from pymicroservice.errors import ConfigurationError

__all__ = [
    'PyMicroService'
]


class PyMicroService(ABC):
    name = None

    def __init__(self):
        self._adapters = []
        self._thread_pool = None
        self._adapter_threads = []

        self._endpoints = []

        self.logger = init_default_logger()
        self.logger.info("Starting")

    def add_adapter(self, adapter):
        self._adapters.append(adapter)

    def start(self):
        self.validate_state()
        self.gather_endpoints()
        self._thread_pool = ThreadPool(len(self._adapters))
        for adapter in self._adapters:

            for endpoint in self._endpoints:
                adapter.register_endpoint(endpoint)

            async_result = self._thread_pool.apply_async(adapter.serve)
            self._adapter_threads.append(async_result)

        for adapter_thread in self._adapter_threads:
            adapter_thread.wait()

    def gather_endpoints(self):
        self.logger.debug("Gathering endpoints")
        for item_name in dir(self):
            if not hasattr(self, item_name):
                continue

            item = getattr(self, item_name)
            if getattr(item, "__is_endpoint__", False) is True:
                self.logger.debug("\tDiscovered endpoint {}".format(item.__name__))
                self._endpoints.append(item)

    def validate_state(self):
        if len(self._adapters) == 0:
            raise ConfigurationError("At least one adapter needed")
        if self.name is None:
            raise ConfigurationError("Name of the microservice not set")
