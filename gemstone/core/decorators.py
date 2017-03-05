import tornado.gen

__all__ = [
    'public_method',
    'private_api_method'
]


def public_method(func):
    """
    Decorates a method to be exposed from a :py:class:`gemstone.PyMicroService` concrete
    implementation. The exposed method will be public.
    """
    func.__is_exposed_method__ = True
    func.is_private = False
    return func


def private_api_method(func):
    """
    Decorates a method to be exposed (privately) from a :py:class:`gemstone.PyMicroService`
    concrete implementation. The exposed method will be private.
    """
    func.__private_api_method__ = True
    func.is_private = True
    return func


def event_handler(event_name):
    """
    Decorator for designating a handler for an event type. ``event_name`` must be a string
    representing the name of the event type.

    The decorated function must accept a parameter: the body of the received event,
    which will be a Python object that can be encoded as a JSON (dict, list, str, int,
    bool, float or None)

    :param event_name:
    :return:
    """

    def wrapper(func):
        func.__is_event_handler__ = True
        func.__handled_event__ = event_name
        return func

    return wrapper


def requires_handler_reference(func):
    """
    Marks a method tha requires access to the :py:class:`gemstone.TornadoJsonRpcHandler` instance
    when calling the request. If a method is decorated with this, when it is called it will
    receive a ``handler`` argument as the first argument.

    Useful when you need to do specific operations such as setting a cookie,
    setting a secure cookie, get the ``current_user`` of the request, etc.
    """
    func.__requires_handler_reference__ = True
    return func


def async_method(func):
    """
    Marks a function as a Tornado generator (coroutine)
    """
    func.__is_async_method__ = True
    return tornado.gen.coroutine(func)
