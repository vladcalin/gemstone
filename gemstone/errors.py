class GemstoneError(Exception):
    pass


class ServiceConfigurationError(GemstoneError):
    pass


class AccessDeniedError(GemstoneError):
    pass


class CalledServiceError(GemstoneError):
    pass
