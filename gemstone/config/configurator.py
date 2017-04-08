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

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    def __str__(self):
        return repr(self)


class CommandLineConfigurator(BaseConfigurator):
    """
    Configurator that collects values from command line arguments.
    For each registered configurable, will attempt to get from command line
    the value designated by the argument ``--name`` where ``name`` is the name of the
    configurable.

    Example

    For the configurables

        - Configurator("a")
        - Configurator("b")
        - Configurator("c")

    the following command line interface will be exposed

    ::

        usage: service.py [-h] [--a A] [--b B] [--c C]

        optional arguments:
          -h, --help  show this help message and exit
          --a A
          --b B
          --c C

    The ``service.py`` can be called like this

    ::

        python service.py --a=1 --b=2 --c=3


    """

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

        configurable.set_value(value)
        return configurable.get_final_value()
