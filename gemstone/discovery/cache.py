import time
import threading


class DummyCache(object):
    """
    Dummy remote service cache. Always returns ``None`` which triggers a
    service registry query.

    Example usage:

    ::

        class MyMicroService(MicroService):
            # ...
            service_registry_cache = DummyCache()
            # ...

    """
    def __init__(self):
        pass

    def add_entry(self, name, remote_service):
        pass

    def get_entry(self, name):
        pass


class CacheEntry(object):
    def __init__(self, name, remote_service):
        self.created = time.time()
        self.name = name
        self.remote_service = remote_service

    def is_still_valid(self, max_age):
        return (time.time() - self.created) < max_age


class ServiceDiscoveryCache(object):
    def __init__(self, cache_lifetime_in_seconds):
        """
        Service discovery cache that keeps entries in memory for
        a constant period of time.

        Example usage:

        ::

            class MyMicroService(MicroService):
                # ...
                service_registry_cache = ServiceDiscoveryCache(60)  # keeps entries for one minute
                # ...

        :param cache_lifetime_in_seconds: int that specifies the cache entry lifetime
        """

        self.ttl = cache_lifetime_in_seconds
        self.container = {}
        self.container_lock = threading.Lock()

    def add_entry(self, name, remote_service):
        with self.container_lock:
            self.container.setdefault(name, [])
            self.container[name].append(CacheEntry(name, remote_service))

    def get_entry(self, name):
        self.expire_entries()

        with self.container_lock:
            for entry in self.container.get(name, []):
                if entry.is_still_valid(self.ttl):
                    return entry

    def expire_entries(self):
        with self.container_lock:
            for _, entries in self.container.items():
                i = 0
                while i < len(entries):
                    current = entries[i]
                    if current.is_still_valid(self.ttl):
                        i += 1
                    else:
                        del entries[i]
