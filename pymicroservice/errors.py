class PyMicroServiceError(Exception):
    pass


class ServiceConfigurationError(PyMicroServiceError):
    pass


class AccessDeniedError(PyMicroServiceError):
    pass


class CalledServiceError(PyMicroServiceError):
    pass