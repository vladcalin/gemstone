from gemstone.core.microservice import MicroService

import abc

from gemstone.plugins.error import MissingPluginNameError


class BasePlugin(abc.ABC):
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
        pass

    def on_service_stop(self):
        pass

    def on_method_call(self, jsonrpc_request):
        pass

    def on_internal_error(self, exc_instance):
        pass
