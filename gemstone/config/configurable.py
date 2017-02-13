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
        self.name = name
        self.mappings = mappings or {}
        self.template = template or (lambda x: x)
        self.value = None
        self.type = type
