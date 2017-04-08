.. _service-discovery:

Service discovery
=================

Enabling automatic service discovery
------------------------------------

In order to enable automatic service discovery, you need to define at least one
discovery strategy.

::

    class ExampleService(gemstone.MicroService):
        # ...
        discovery_strategies = [
            gemstone.discovery.RedisDiscoveryStrategy("redis://registry.example.com:6379/0"),
            # ...
        ]
        # ...


Using service discovery
-----------------------

You can use the :py:meth:`gemstone.MicroService.get_service` method to automatically
discover other microservice that uses at least one discovery strategy as your service does,
and interact with it directly.

Example

::

    # ...
    remote_service = self.get_service("user_manager_service")
    if not remote_service:
        raise RuntimeError("Service could not be located")

    res = remote_service.call_method("find_user", {"username": "example"}
    # ...

The :py:meth:`gemstone.MicroService.get_service` method returns a :py:meth:`gemstone.RemoteService`
instance. See :ref:`gemstone_client` for more information on this topic.
