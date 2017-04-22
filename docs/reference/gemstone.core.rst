The gemstone.core module
========================


.. automodule:: gemstone.core

The gemstone.core.MicroService class
------------------------------------

    .. autoclass:: gemstone.core.MicroService

        .. autoattribute:: gemstone.core.MicroService.name
        .. autoattribute:: gemstone.core.MicroService.host
        .. autoattribute:: gemstone.core.MicroService.port
        .. autoattribute:: gemstone.core.MicroService.accessible_at
        .. autoattribute:: gemstone.core.MicroService.endpoint
        .. autoattribute:: gemstone.core.MicroService.template_dir
        .. autoattribute:: gemstone.core.MicroService.static_dirs
        .. autoattribute:: gemstone.core.MicroService.extra_handlers
        .. autoattribute:: gemstone.core.MicroService.plugins
        .. autoattribute:: gemstone.core.MicroService.discovery_strategies
        .. autoattribute:: gemstone.core.MicroService.service_registry_ping_interval
        .. autoattribute:: gemstone.core.MicroService.periodic_tasks
        .. autoattribute:: gemstone.core.MicroService.event_transports
        .. autoattribute:: gemstone.core.MicroService.configurables
        .. autoattribute:: gemstone.core.MicroService.configurators
        .. autoattribute:: gemstone.core.MicroService.max_parallel_blocking_tasks

Can be called
"""""""""""""

        .. automethod:: gemstone.core.MicroService.get_service
        .. automethod:: gemstone.core.MicroService.emit_event
        .. automethod:: gemstone.core.MicroService.get_io_loop
        .. automethod:: gemstone.core.MicroService.get_executor
        .. automethod:: gemstone.core.MicroService.start
        .. automethod:: gemstone.core.MicroService.configure
        .. automethod:: gemstone.core.MicroService.register_plugin
        .. automethod:: gemstone.core.MicroService.get_plugin
        .. automethod:: gemstone.core.MicroService.start_thread
        .. automethod:: gemstone.core.MicroService.make_tornado_app

Can be overridden
"""""""""""""""""

        .. automethod:: gemstone.core.MicroService.get_logger
        .. automethod:: gemstone.core.MicroService.authenticate_request
        .. automethod:: gemstone.core.MicroService.on_service_start

The gemstone.core.Container class
---------------------------------


    .. autoclass:: gemstone.core.Container
        :members:

        .. py:attribute:: microservice

Decorators
----------

    .. autofunction:: gemstone.core.exposed_method
    .. autofunction:: gemstone.core.event_handler

