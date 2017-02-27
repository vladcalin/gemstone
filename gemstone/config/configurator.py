import abc
import argparse

import simplejson as json


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


class JsonFileConfigurator(BaseConfigurator):
    def __init__(self, file_name=None, from_cmd_arg=None):
        if file_name and from_cmd_arg:
            raise ValueError("Only one of 'file_name' and "
                             "'from_cmd_arg' supported")

        super(JsonFileConfigurator, self).__init__()
        self.file_name = file_name
        self.from_cmd_arg = from_cmd_arg
        self.data = None

    def get(self, name):
        # TODO: implement this
        pass

    def load(self):
        if self.file_name:
            self.data = self._load_from_file(self.file_name)
        elif self.from_cmd_arg:
            self.data = self._load_from_cmd_line()

    def _load_from_file(self, file_name):
        with open(file_name) as f:
            return json.load(f)

    def _load_from_cmd_line(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("file_name")
        args = parser.parse_args()
        return self._load_from_file(args.file_name)
