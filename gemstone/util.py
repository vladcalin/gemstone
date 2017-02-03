import sys
import logging


def init_default_logger():
    logging.basicConfig(
        level=logging.DEBUG,
    )
    return logging.getLogger()


def as_completed(*async_result_wrappers):
    """
    Yields results as they become available.

    :param async_result_wrappers: :py:class:`gemstone.client.remote_service.AsyncMethodCall` instances.
    :return: a generator that yields items as soon they results become available.
    """

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
    rest

    :param async_result_wrappers:
    :return:
    """
    wrappers_copy = list(async_result_wrappers)
    while True:
        completed = list(filter(lambda x: x.finished(), wrappers_copy))
        if not len(completed):
            continue

        return completed[0]


def make_callbacks(async_result_wrappers, on_result, on_error):
    for item in as_completed(*async_result_wrappers):
        if item.error():
            on_error(item.error())
        else:
            on_result(item.result())
