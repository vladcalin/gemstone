The ``gemstone`` module (main classes)
======================================

Core classes
------------

.. py:currentmodule:: gemstone

.. autoclass:: MicroService

Attributes
~~~~~~~~~~

You can (and should) define various class attributes in order
to provide the desired functionality for your microservice.
These attributes can be configured at runtime by using
the configurable sub-framework (read more at :ref:`configuration-tips` )


Identification
^^^^^^^^^^^^^^

    .. autoattribute:: gemstone.MicroService.name
    .. autoattribute:: gemstone.MicroService.host
    .. autoattribute:: gemstone.MicroService.port
    .. autoattribute:: gemstone.MicroService.endpoint
    .. autoattribute:: gemstone.MicroService.accessible_at

Access validation
^^^^^^^^^^^^^^^^^

    .. autoattribute:: gemstone.MicroService.validation_strategies

Event dispatching
^^^^^^^^^^^^^^^^^

    .. autoattribute:: gemstone.MicroService.event_transports

Dynamic configuration
^^^^^^^^^^^^^^^^^^^^^

    .. autoattribute:: gemstone.MicroService.skip_configuration
    .. autoattribute:: gemstone.MicroService.configurables
    .. autoattribute:: gemstone.MicroService.configurators

Web application functionality
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    .. autoattribute:: gemstone.MicroService.extra_handlers
    .. autoattribute:: gemstone.MicroService.template_dir
    .. autoattribute:: gemstone.MicroService.static_dirs

Periodic tasks
^^^^^^^^^^^^^^

    .. autoattribute:: gemstone.MicroService.periodic_tasks

Service auto-discovery
^^^^^^^^^^^^^^^^^^^^^^

    .. autoattribute:: gemstone.MicroService.service_registry_urls
    .. autoattribute:: gemstone.MicroService.service_registry_ping_interval

Misc
^^^^

    .. autoattribute:: gemstone.MicroService.max_parallel_blocking_tasks

Methods
~~~~~~~

Can be overridden
^^^^^^^^^^^^^^^^^

    .. automethod:: gemstone.MicroService.on_service_start
    .. automethod:: gemstone.MicroService.api_token_is_valid
    .. automethod:: gemstone.MicroService.get_logger

Can be called
^^^^^^^^^^^^^

    .. automethod:: gemstone.MicroService.get_service
    .. automethod:: gemstone.MicroService.start_thread
    .. automethod:: gemstone.MicroService.emit_event
    .. automethod:: gemstone.MicroService.get_current_configuration
    .. automethod:: gemstone.MicroService.make_tornado_app
    .. automethod:: gemstone.MicroService.start



.. autoclass:: RemoteService

    .. autoattribute:: gemstone.RemoteService.methods
    .. autoattribute:: gemstone.RemoteService.notifications



Decorators
----------

.. autofunction:: public_method
.. autofunction:: private_api_method
.. autofunction:: event_handler

Request handlers
----------------

.. autoclass:: GemstoneCustomHandler

.. autoclass:: TornadoJsonRpcHandler
    :members:
