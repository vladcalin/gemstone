import functools
import re

import tornado.gen

__all__ = [
    'event_handler',
    'exposed_method'
]

METHOD_NAME_REGEX = re.compile(r'^[a-zA-Z][a-zA-Z0-9_.]*$')


def event_handler(event_name):
    """
    Decorator for designating a handler for an event type. ``event_name`` must be a string
    representing the name of the event type.

    The decorated function must accept a parameter: the body of the received event,
    which will be a Python object that can be encoded as a JSON (dict, list, str, int,
    bool, float or None)

    :param event_name: The name of the event that will be handled. Only one handler per
                       event name is supported by the same microservice.
    """

    def wrapper(func):
        func._event_handler = True
        func._handled_event = event_name
        return func

    return wrapper


def exposed_method(name=None, private=False, is_coroutine=True, requires_handler_reference=False):
    """
    Marks a method as exposed via JSON RPC.

    :param name: the name of the exposed method. Must contains only letters, digits, dots and underscores.
                 If not present or is set explicitly to ``None``, this parameter will default to the name
                 of the exposed method.
                 If two methods with the same name are exposed, a ``ValueError`` is raised.
    :type name: str
    :param private: Flag that specifies if the exposed method is private.
    :type private: bool
    :param is_coroutine: Flag that specifies if the method is a Tornado coroutine. If True, it will be wrapped
                         with the :py:func:`tornado.gen.coroutine` decorator.
    :type is_coroutine: bool
    :param requires_handler_reference: If ``True``, the handler method will receive as the first
                                       parameter a ``handler`` argument with the Tornado
                                       request handler for the current request. This request handler
                                       can be further used to extract various information from the
                                       request, such as headers, cookies, etc.
    :type requires_handler_reference: bool

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
            real_wrapper.__gemstone_is_coroutine = True
            real_wrapper = tornado.gen.coroutine(real_wrapper)
            setattr(real_wrapper, "_is_coroutine", True)

        if requires_handler_reference:
            setattr(real_wrapper, "_req_h_ref", True)

        setattr(real_wrapper, "_exposed_name", method_name)

        return real_wrapper

    return wrapper
