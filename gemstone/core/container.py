import abc
import inspect


class Container(abc.ABC):
    """
    A container for exposed methods and/or event handlers
    for a better modularization of the application.

    Example usage

    ::

        # in users.py

        class UsersModule(gemstone.Container):

            @gemstone.exposed_method("users.register")
            def users_register(self, username, password):
                pass

            @gemstone.exposed_method("users.login")
            def users_login(self)

    """

    def __init__(self):
        self.microservice = None

    def set_microservice(self, microservice):
        self.microservice = microservice

    def get_executor(self):
        return self.microservice.get_executor()

    def get_exposed_methods(self):
        exposed = []
        for item in self._iter_methods():
            if getattr(item, "_exposed_public", False) or \
                    getattr(item, "_exposed_private", False):
                exposed.append(item)
        return exposed

    def get_event_handlers(self):
        handlers = []
        for item in self._iter_methods():
            if getattr(item, "_event_handlers", False):
                handlers.append(item)
        return handlers

    def _iter_methods(self):
        for item_name in dir(self):
            item = getattr(self, item_name)
            if callable(item):
                yield item
