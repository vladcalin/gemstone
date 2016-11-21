import sqlite3

from pymicroservice.core.microservice import PyMicroService
from pymicroservice.core.decorators import endpoint


class ServiceRegistry(PyMicroService):
    name = "pymicroservice.builtin.registry"
    services = {

    }

    def __init__(self):
        super(ServiceRegistry, self).__init__()

    @endpoint
    def register_service(self, name, location):
        if name not in self.services:
            self.services[name] = location
        return "ok"

    @endpoint
    def unregister_service(self, name):
        if name in self.services:
            raise ValueError("Service not registered")

        del self.services[name]
        return "ok"

    @endpoint
    def locate_service(self, name):
        return self.services.get(name)


if __name__ == '__main__':
    registry = ServiceRegistry()
    registry.start()
