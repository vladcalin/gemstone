from gemstone.core.microservice import MicroService

import abc

from gemstone.plugins.error import MissingPluginNameError


class BasePlugin(abc.ABC):
    """
    Base class for creating a plugin.

    """

    #: The name of the plugin. Must be unique per microservice.
    name = None

    def __init__(self):
        self.microservice = None

        if self.name is None:
            raise MissingPluginNameError("Instance {} does not have a name".format(self))

    def set_microservice(self, microservice: MicroService):
        if not isinstance(microservice, MicroService):
            raise ValueError(
                "Expected gemstone.core.microservice.MicroService but got {} instead".format(
                    microservice.__class__.__name__
                ))

        self.microservice = microservice

    def on_service_start(self):
        """
        Called once when the microservice starts, after it completed all the initialization
        steps
        """
        pass

    def on_service_stop(self):
        """
        Called once when the microservice stops.
        """
        pass

    def on_method_call(self, jsonrpc_request):
        """
        Called for every method call (even in batch requests, this method will be called
        for every request in batch).

        :param jsonrpc_request: a :py:class:`JsonRpcRequest` instance.
        """
        pass

    def on_internal_error(self, exc_instance):
        """
        Called when an internal error occurs when a method was called.

        :param exc_instance: The caught :py:class:`Exception` instance.
        """
