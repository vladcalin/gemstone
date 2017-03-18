class GemstoneError(Exception):
    pass


class ServiceConfigurationError(GemstoneError):
    pass


# RemoteService related exception

class RemoteServiceError(GemstoneError):
    pass


class CalledServiceError(RemoteServiceError):
    pass


class MethodNotFoundError(RemoteServiceError):
    pass


class InvalidParamsError(RemoteServiceError):
    pass


class AccessDeniedError(RemoteServiceError):
    pass


class InternalErrorError(RemoteServiceError):
    pass


class UnknownError(RemoteServiceError):
    pass
