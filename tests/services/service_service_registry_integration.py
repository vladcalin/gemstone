from gemstone import MicroService


class TestServiceNoServiceRegistries(MicroService):
    name = "test.service.1"


class TestServiceOneServiceRegistry(MicroService):
    name = "test.service.1"
    service_registry_urls = ["http://localhost:9999/api"]
