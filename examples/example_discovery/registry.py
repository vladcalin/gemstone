import threading

import gemstone


class ServiceRegistry(gemstone.MicroService):
    name = "service_registry"

    port = 8080

    services = {}
    lock = threading.Lock()

    @gemstone.exposed_method()
    def ping(self, name, url):
        with self.lock:
            self.services[name] = url

    @gemstone.exposed_method()
    def locate_service(self, name):
        with self.lock:
            location = self.services.get(name)
            if location:
                return [location]
            else:
                return []


if __name__ == '__main__':
    ServiceRegistry().start()
