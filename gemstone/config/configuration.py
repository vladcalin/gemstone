import argparse
import os
import abc


class LazyValue(abc.ABC):
    def __init__(self, name, *, template=None):
        self.name = name
        if template:
            self.template = template
        else:
            self.template = lambda x: x

    @abc.abstractmethod
    def get_value(self):
        pass


class LazyEnvironmentValue(LazyValue):
    def get_value(self):
        return self.template(os.environ.get(self.name))


class Configuration(object):
    def __init__(self, config_dict):
        self._config_dict = config_dict

    def get_all_option_names(self):
        return list(self._config_dict.keys())

    def get_option(self, option_name):
        return self._resolve_option(option_name)

    def _resolve_option(self, option_name):
        if option_name not in self._config_dict:
            raise ValueError("{} is not defined".format(option_name))
        val = self._config_dict.get(option_name)
        if isinstance(val, LazyValue):
            return val.get_value()
        else:
            return val

    @classmethod
    def from_env(cls, env_var_name, template=None):
        return LazyEnvironmentValue(env_var_name, template=template)
