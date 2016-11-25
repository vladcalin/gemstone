__all__ = [
    'exposed_method'
]


def exposed_method(func):
    func.__is_exposed_method__ = True
    return func
