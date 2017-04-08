import logging

from gemstone.client.structs import AsyncMethodCall


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
    Just like :py:func:`gemstone.as_completed`, but returns only the first item and discards the
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
