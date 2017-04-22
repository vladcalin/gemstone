import abc


class BaseDiscoveryStrategy(abc.ABC):
    """
    Base class for service discovery strategies.
    """
    @abc.abstractmethod
    def ping(self, name, location, **kwargs):
        """
        Pings the service registry as defined by the implemented protocol with the
        necessary information about the service location.

        :param name: The name of the microservice
        :param location: The HTTP location of the microservice, where it can be accessed (multiple
                         microservices might have the same location, for example when they
                         are deployed behind a reverse proxy)
        :return:
        """
        pass

    @abc.abstractmethod
    def locate(self, name):
        """
        Attempts to locate a microservice with the given name. If no such service exists,
        must return ``None``

        :param name: The name of the microservice to be located
        :return: a list of str with the URLs where a microservice with the given name can
                 be found.
        """
        pass
