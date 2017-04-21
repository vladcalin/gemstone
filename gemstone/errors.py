class GemstoneError(Exception):
    pass


class ServiceConfigurationError(GemstoneError):
    pass


# RemoteService related exception

class RemoteServiceError(GemstoneError):
    pass


class CalledServiceError(RemoteServiceError):
    pass


# Plugin specific

class PluginDoesNotExistError(GemstoneError):
    """
    Raised when a plugin is queried but no plugin with the
    specified name exists.
    """
    pass
