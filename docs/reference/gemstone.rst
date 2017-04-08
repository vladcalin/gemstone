Core classes
============

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


    .. seealso:: :ref:`private_methods`

Event dispatching
^^^^^^^^^^^^^^^^^

    .. autoattribute:: gemstone.MicroService.event_transports

    .. seealso::
        - :ref:`publisher-subscriber`
        - :ref:`event-transports`

Dynamic configuration
^^^^^^^^^^^^^^^^^^^^^

    .. autoattribute:: gemstone.MicroService.configurables
    .. autoattribute:: gemstone.MicroService.configurators

    .. seealso:: :ref:`configurable-framework`


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

    .. autoattribute:: gemstone.MicroService.discovery_strategies
    .. autoattribute:: gemstone.MicroService.service_registry_ping_interval

Misc
^^^^

    .. autoattribute:: gemstone.MicroService.max_parallel_blocking_tasks
    .. autoattribute:: gemstone.MicroService.modules


Methods
~~~~~~~

Can be overridden
^^^^^^^^^^^^^^^^^

    .. automethod:: gemstone.MicroService.on_service_start
    .. automethod:: gemstone.MicroService.get_logger

Can be called
^^^^^^^^^^^^^

    .. automethod:: gemstone.MicroService.get_service
    .. automethod:: gemstone.MicroService.start_thread
    .. automethod:: gemstone.MicroService.emit_event
    .. automethod:: gemstone.MicroService.get_current_configuration
    .. automethod:: gemstone.MicroService.make_tornado_app
    .. automethod:: gemstone.MicroService.start
    .. automethod:: gemstone.MicroService.configure



.. autoclass:: RemoteService

    .. autoattribute:: gemstone.RemoteService.call_method
    .. autoattribute:: gemstone.RemoteService.call_method_async
    .. autoattribute:: gemstone.RemoteService.notify
    .. autoattribute:: gemstone.RemoteService.call_batch



Decorators
----------

.. autofunction:: exposed_method
.. autofunction:: event_handler


Request handlers
----------------

.. autoclass:: GemstoneCustomHandler

.. autoclass:: TornadoJsonRpcHandler
    :members:
