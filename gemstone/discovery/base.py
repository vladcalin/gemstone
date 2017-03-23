import abc


class BaseDiscoveryStrategy(abc.ABC):
    @abc.abstractmethod
    def ping(self, name, location, **kwargs):
        pass

    @abc.abstractmethod
    def locate(self, name):
        pass
