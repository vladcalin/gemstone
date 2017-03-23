import time
import threading


class CacheEntry(object):
    def __init__(self, name, remote_service):
        self.created = time.time()
        self.name = name
        self.remote_service = remote_service

    def is_still_valid(self, max_age):
        return (time.time() - self.created) < max_age


class ServiceDiscoveryCache(object):
    def __init__(self, cache_lifetime):
        self.ttl = cache_lifetime
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
