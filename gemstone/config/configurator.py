import abc
import argparse


class BaseConfigurator(abc.ABC):
    """
    Base class for defining configurators. A configurator is a class that, starting
    from a set of name-configurable pairs, depending on the configurables' options
    and the environment, builds a configuration for the application.

    """

    def __init__(self):
        self.configurables = []

    @abc.abstractmethod
    def load(self):
        """
        Loads the configuration for the application
        """
        pass

    @abc.abstractmethod
    def get(self, name):
        pass

    def register_configurable(self, configurable):
        self.configurables.append(configurable)

    def get_configurable_by_name(self, name):
        l = [c for c in self.configurables if c.name == name]
        if l:
            return l[0]


class CommandLineConfigurator(BaseConfigurator):
    def __init__(self):
        super(CommandLineConfigurator, self).__init__()
        self.args = None

    def load(self):
        parser = argparse.ArgumentParser()
        for configurable in self.configurables:
            parser.add_argument("--" + configurable.name)
        self.args = parser.parse_args()

    def get(self, name):
        configurable = self.get_configurable_by_name(name)
        if not configurable:
            return None

        value = getattr(self.args, name, None)
        if not value:
            return None

        value = configurable.template(value)
        if value in configurable.mappings:
            return configurable.mappings[value](value)

        return value
