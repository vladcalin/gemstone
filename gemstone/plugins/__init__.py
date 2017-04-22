"""

This module provides various tools to create general use plugins for the microservice.

A plugin can override specific attributes from the :py:class:`BasePlugin` class that will
be called in specific situations.

Also, a plugin can define extra methods that can be used later inside the method calls,
as shown in the following example:

::

    @gemstone.core.exposed_method()
    def say_hello(self, name):
        self.get_plugin("remote_logging").log_info("Somebody said hello to {}".format(name))
        return True

"""

from .base import BasePlugin
from .error import MissingPluginNameError, PluginError

__all__ = [
    'BasePlugin',

    'MissingPluginNameError',
    'PluginError'
]
