import abc


class Container(abc.ABC):
    """
    A container for exposed methods and/or event handlers
    for a better modularization of the application.

    Example usage

    ::

        # in users.py

        class UsersModule(gemstone.Module):

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
