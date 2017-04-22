import logging
import importlib

from gemstone.client import RemoteService, AsyncMethodCall


def init_default_logger():
    logging.basicConfig(
        level=logging.DEBUG,
    )
    return logging.getLogger()


def as_completed(*async_result_wrappers):
    """
    Yields results as they become available from asynchronous method calls.

    Example usage

    ::

        async_calls = [service.call_method_async("do_stuff", (x,)) for x in range(25)]

        for async_call in gemstone.as_completed(*async_calls):
            print("just finished with result ", async_call.result())

    :param async_result_wrappers: :py:class:`gemstone.client.structs.AsyncMethodCall` instances.
    :return: a generator that yields items as soon they results become available.

    .. versionadded:: 0.5.0
    """
    for item in async_result_wrappers:
        if not isinstance(item, AsyncMethodCall):
            raise TypeError("Got non-AsyncMethodCall object: {}".format(item))

    wrappers_copy = list(async_result_wrappers)

    while len(wrappers_copy):
        completed = list(filter(lambda x: x.finished(), wrappers_copy))
        if not len(completed):
            continue

        for item in completed:
            wrappers_copy.remove(item)
            yield item


def first_completed(*async_result_wrappers):
    """
    Just like :py:func:`as_completed`, but returns only the first item and discards the
    rest.

    :param async_result_wrappers:
    :return:

    .. versionadded:: 0.5.0
    """
    for item in async_result_wrappers:
        if not isinstance(item, AsyncMethodCall):
            raise TypeError("Got non-AsyncMethodCall object: {}".format(item))
    wrappers_copy = list(async_result_wrappers)
    while True:
        completed = list(filter(lambda x: x.finished(), wrappers_copy))
        if not len(completed):
            continue

        return completed[0].result()


def get_remote_service_instance_for_url(url):
    return RemoteService(url)


def dynamic_load(module_or_member):
    """
    Dynamically loads a class or member of a class.

    If ``module_or_member`` is something like ``"a.b.c"``, will perform ``from a.b import c``.

    If ``module_or_member`` is something like ``"a"`` will perform ``import a``

    :param module_or_member: the name of a module or member of a module to import.
    :return: the returned entity, be it a module or member of a module.
    """
    parts = module_or_member.split(".")
    if len(parts) > 1:
        name_to_import = parts[-1]
        module_to_import = ".".join(parts[:-1])
    else:
        name_to_import = None
        module_to_import = module_or_member

    module = importlib.import_module(module_to_import)
    if name_to_import:
        to_return = getattr(module, name_to_import)
        if not to_return:
            raise AttributeError("{} has no attribute {}".format(module, name_to_import))
        return to_return
    else:
        return module
