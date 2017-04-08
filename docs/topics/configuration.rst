.. _configuration-tips:

Configurable features
=====================

In the context of this framework, configurables are
entities that designate what properties of the microservice
can be dynamically set and configurators are strategies
that, on service startup, collects the required
properties from the environment.

Currently, the available confugurators are:

- :py:class:`gemstone.config.configurator.CommandLineConfigurator` - collects values from
  the command line arguments

In order to specify configurables for the microservice, you have to provide
set the :py:data:`gemstone.MicroService.configurables` attribute to a list of
:py:class:`Configurable` objects.

Configurators are specified in the :py:data:`gemstone.MicroService.configurators` attribute.
On service startup, each configurator tries to extract the required values from the environment in
the order they are defined.


In order to trigger the configurators, you need to explicitly call the
:py:meth:`gemstone.MicroService.configure` method before calling
:py:meth:`gemstone.MicroService.start`

Defining configurators
----------------------

Configurators are defined in the :py:attr:`gemstone.MicroService.configurators` class attribute.

::

    class ExampleService(gemstone.MicroService):
        # ...
        configurators = [
            gemstone.config.CommandLineConfigurator()
        ]
        # ...

Defining configurables
----------------------

Configurables are defined in the :py:attr:`gemstone.MicroService.configurables` class attribute.

::

    class ExampleService(gemstone.MicroService):
        # ...
        configurables = [
            gemstone.config.Configurable("port", template=lambda x: int(x)),
            gemstone.config.Configurable("discovery_strategies",
                                         template=lambda x: [RedisDiscoveryStrategy(a) for a in x.split(",")]),
            gemstone.config.Configurable("host"),
            gemstone.config.Configurable("accessible_at"),
        ]
        # ...

In the example above, we defined 4 configurables:

- ``gemstone.config.Configurable("port", template=lambda x: int(x))`` the ``--port`` command-line
  argument will be casted to ``int`` and assigned to ``gemstone.MicroService.port``
- ``gemstone.config.Configurable("host")`` the ``--host`` command-line
  argument assigned to ``gemstone.MicroService.host``