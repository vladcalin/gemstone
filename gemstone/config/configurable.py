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
            Configurable("port", type=int, mappings={
                "random": random.randint(8000, 65000)
            }),
            Configurable("host", type=str)
        ]
        configurators = [
            CommandLineConfigurator(),
            IniFileConfigurator("config.ini"),
            JsonFileConfigurator("config.json"),
            XmlFileConfigurator("config.xml")
        ]

When :py:meth:`Microservice.start` is called, the configurators
search for values that can override the specified configurables defaults.

The configurators resolve in the order they are declared, meaning that a value
that was set by a configurator can be overriden by a configurator that is

"""


class Configurable(object):
    def __init__(self, name, type=str, *, template=None, mappings=None):
        """
        Defines a configurable value for the application.

        The order of the applied transformations on the extracted value is:

        1. the type
        2. the template
        3. the mappings

        :param name: The name of the configurable parameter
        :param type: The type of the configurable parameter
        :param template: A callable template to apply over the raw extracted value
        :param mappings: A List of tuples of (possible_value, template_callable_or_constants) which
                         specifies special behaviour depending on the extracted value
        """
        self.name = name
        self.mappings = mappings or []
        self.template = template or (lambda x: x)
        self.value = None
        self.type = type

    def set_value(self, value):
        self.value = self.type(value)

    def _get_mapping(self, for_value):
        for val_name, mapping in self.mappings:
            if val_name == for_value:
                return mapping
        return lambda x: x

    def get_final_value(self):
        to_return = self.template(self.value)
        mapping = self._get_mapping(to_return)
        if callable(mapping):
            return mapping(to_return)
        else:
            return mapping

    def __repr__(self):
        return "<Configurable name={} type={}>".format(self.name, self.type)

    def __str__(self):
        return repr(self)
