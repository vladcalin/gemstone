.. _configurable-framework:

Configurables and configurators
===============================

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




Configurable
------------

.. py:currentmodule:: gemstone.config.configurable

.. autoclass:: Configurable
    :members:


Configurators
-------------

.. py:currentmodule:: gemstone.config.configurator

.. autoclass:: BaseConfigurator
    :members:

.. autoclass:: CommandLineConfigurator
    :members:


