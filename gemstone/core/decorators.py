import functools
import re
import inspect

import tornado.gen

__all__ = [
    'event_handler',
    'exposed_method'
]


def public_method(func):
    """
    Decorates a method to be exposed from a :py:class:`gemstone.PyMicroService` concrete
    implementation. The exposed method will be public.

    .. deprecated:: 0.9.0
        Use :py:func:`exposed_method` instead.

    """
    func.__gemstone_internal_public = True
    return func


def private_api_method(func):
    """
    Decorates a method to be exposed (privately) from a :py:class:`gemstone.PyMicroService`
    concrete implementation. The exposed method will be private.

    .. deprecated:: 0.9.0
        Use :py:func:`exposed_method` instead.

    """
    func.__gemstone_internal_private = True
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
        func._event_handler = True
        func._handled_event = event_name
        return func

    return wrapper


def requires_handler_reference(func):
    """
    Marks a method tha requires access to the :py:class:`gemstone.TornadoJsonRpcHandler` instance
    when calling the request. If a method is decorated with this, when it is called it will
    receive a ``handler`` argument as the first argument.

    Useful when you need to do specific operations such as setting a cookie,
    setting a secure cookie, get the ``current_user`` of the request, etc.

    .. deprecated:: 0.9.0
        Use :py:func:`exposed_method` instead.

    """
    func.__gemstone_internal_req_h_ref = True
    return func


def async_method(func):
    """
    Marks a function as a Tornado generator (coroutine)

    .. deprecated:: 0.9.0
        Use :py:func:`exposed_method` instead.

    """
    func.__gemstone_is_coroutine = True
    return tornado.gen.coroutine(func)


METHOD_NAME_REGEX = re.compile(r'^[a-zA-Z][a-zA-Z0-9_.]*$')


def exposed_method(name=None, private=False, is_coroutine=True, requires_handler_reference=False,
                   **kwargs):
    """
    Marks a method as exposed via JSON RPC.

    :param name: the name of the exposed method. Must contains only letters, digits, dots and underscores.
                 If not present or is set explicitly to ``None``, this parameter will default to the name
                 of the exposed method.
                 If two methods with the same name are exposed, a ``ValueError`` is raised.
    :param public: Flag that specifies if the exposed method is public (can be accessed without token)
    :param private: Flag that specifies if the exposed method is private.
    :param is_coroutine: Flag that specifies if the method is a Tornado coroutine. If True, it will be wrapped
                         with the :py:func:`tornado.gen.coroutine` decorator.
    :param kwargs: Not used.

    .. versionadded:: 0.9.0

    """

    def wrapper(func):

        # validation

        if name:
            method_name = name
        else:
            method_name = func.__name__

        if not METHOD_NAME_REGEX.match(method_name):
            raise ValueError("Invalid method name: '{}'".format(method_name))

        @functools.wraps(func)
        def real_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # set appropriate flags
        if private:
            setattr(real_wrapper, "_exposed_private", True)
        else:
            setattr(real_wrapper, "_exposed_public", True)

        if is_coroutine:
            real_wrapper = async_method(real_wrapper)
            setattr(real_wrapper, "_is_coroutine", True)

        if requires_handler_reference:
            setattr(real_wrapper, "_req_h_ref", True)

        setattr(real_wrapper, "_exposed_name", method_name)

        return real_wrapper

    return wrapper
