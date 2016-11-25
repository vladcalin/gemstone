__all__ = [
    'public_method'
]


def public_method(func):
    func.__is_exposed_method__ = True
    return func


def private_api_method(func):
    func.__private_api_method__ = True
