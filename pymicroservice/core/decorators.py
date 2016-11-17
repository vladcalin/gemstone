def endpoint(func):
    func.__is_endpoint__ = True
    return func
