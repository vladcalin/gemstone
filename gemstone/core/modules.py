import abc


class Module(abc.ABC):
    def __init__(self):
        self.microservice = None

    def set_microservice(self, microservice):
        self.microservice = microservice
