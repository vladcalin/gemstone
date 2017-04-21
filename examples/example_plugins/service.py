from gemstone.core.microservice import MicroService
from gemstone.core.decorators import exposed_method
from gemstone.plugins.base import BasePlugin


class ExamplePlugin(BasePlugin):
    name = "example_plugin"

    def on_service_start(self):
        self.microservice.logger.info("Microservice started!")

    def on_service_stop(self):
        self.microservice.logger.info("Microservice stoped!")

    def on_internal_error(self, exc_instance):
        self.microservice.logger.error("Error!!!!! {}".format(exc_instance))

    def on_method_call(self, jsonrpc_request):
        self.microservice.logger.error("Method called: name={} params={}".format(
            jsonrpc_request.method, jsonrpc_request.params
        ))

        self.microservice.logger.info("Extras: {}".format(jsonrpc_request.extra))

    def custom_method(self):
        self.microservice.logger.warning("Custom method called!")


class ExampleService(MicroService):
    name = "example_service"

    @exposed_method()
    def sum(self, a, b):
        return a + b

    @exposed_method()
    def product(self, a, b):
        self.get_plugin("example_plugin").custom_method()
        return a * b


if __name__ == '__main__':
    service = ExampleService()
    service.register_plugin(ExamplePlugin())
    service.start()
