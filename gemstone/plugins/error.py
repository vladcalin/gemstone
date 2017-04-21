class PluginError(Exception):
    """
    Base class for plugin specific errors
    """
    pass


class MissingPluginNameError(PluginError):
    """
    Raised when a plugin does not have a properly configured name
    """
    pass
