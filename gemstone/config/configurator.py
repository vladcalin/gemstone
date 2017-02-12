import abc


class BaseConfigurator(abc.ABC):
    """
    Base class for defining configurators. A configurator is a class that, starting
    from a set of name-configurable pairs, depending on the configurables' options
    and the environment, builds a configuration for the application.

    """

    def __init__(self):
        self._configurable = {}

    @abc.abstractmethod
    def load(self):
        """
        Loads the configuration for the application
        """
        pass

    @abc.abstractmethod
    def build_config(self):
        """
        Computes the final configuration.

        :return:
        """
        pass

    @abc.abstractmethod
    def get(self, name):
        pass

    def register_configurable(self, name, configurable):
        self._configurable[name] = configurable


class CommandLineConfigurator(BaseConfigurator):
    def __init__(self):
        super(CommandLineConfigurator, self).__init__()

    def load(self):
        pass

    def build_config(self):
        pass

    def get(self, name):
        pass
