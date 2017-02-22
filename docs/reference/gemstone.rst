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
    :members:

    .. autoattribute:: gemstone.RemoteService.methods
        :annotation: = A proxy object through which methods from the remote service can be invoked. Example usage

                        ::

                           client = RemoteService(api_url)
                           result = client.methods.method_to_call(arguments)

    .. autoattribute:: gemstone.RemoteService.notifications
        :annotation: = A proxy object through which methods from the remote service can be invoked as notifications.
                       (no answer is expected). Example usage:

                        ::

                           client = RemoteService(api_url)
                           client.notifications.method_to_call(arguments)  # returns None





Decorators
----------

.. autofunction:: public_method

.. autofunction:: private_api_method

Request handlers
----------------

.. autoclass:: TornadoJsonRpcHandler
    :members:
