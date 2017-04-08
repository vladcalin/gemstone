"""

Configurable component of the configurable sub-framework.

Example usage of configurables

::

    class MyMicroService(MicroService):

        name = "jadasd"
        port = 8000
        host = "127.0.0.1"
        accessible_at = "http://..."
        registry_urls = [...]

        configurables = [
            Configurable("port", template=lambda x: int(x)),
            Configurable("host")
        ]
        configurators = [
            CommandLineConfigurator()
        ]

When :py:meth:`Microservice.configure` is called, the configurators
search for values that can override the specified configurables defaults.

The configurators resolve in the order they are declared.

"""


class Configurable(object):
    def __init__(self, name, *, template=None):
        """
        Defines a configurable value for the application.

        Example (You should not use configurables in this way unless
        you are writing a custom ``Configurator``)

        ::

            c = Configurable("test", template=lambda x: x * 2)
            c.set_value("10")
            c.get_final_value()  # "10" * 2 -> 1010

            c2 = Configurable("list_of_ints", template=lambda x: [int(y) for y in x.split(",")])
            c.set_value("1,2,3,4,5")
            c.get_final_value()  # [1,2,3,4,5]


        :param name: The name of the configurable parameter
        :param template: A callable template to apply over the extracted value
        """
        self.name = name
        self.template = template or (lambda x: x)
        self.value = None

    def set_value(self, value):
        self.value = value

    def get_final_value(self):
        to_return = self.value
        return self.template(to_return)

    def __repr__(self):
        return "<Configurable name={}>".format(self.name)

    def __str__(self):
        return repr(self)
