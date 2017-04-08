import threading
import urllib.parse
import hashlib

import redis

from gemstone.discovery.base import BaseDiscoveryStrategy

_thread_local = threading.local()


class RedisDiscoveryStrategy(BaseDiscoveryStrategy):
    def __init__(self, redis_url, time_to_live=180):
        parsed = urllib.parse.urlparse(redis_url)
        if parsed.scheme != "redis":
            raise ValueError("Invalid scheme: {}".format(parsed.scheme))
        self.host = parsed.hostname
        self.port = parsed.port
        self.db = int(parsed.path[1:])
        self.ttl = time_to_live

        self.connection = self._get_connection()

    def _get_connection(self):
        conn = getattr(_thread_local, "_redisconn", None)
        if conn:
            return conn

        conn = redis.StrictRedis(host=self.host, port=self.port, db=self.db)
        setattr(_thread_local, "_redisconn", conn)
        return conn

    def locate(self, name):
        values = []
        keys = self.connection.keys(name + "#*")
        for key in keys:
            values.append(self.connection.get(key))
        return [x.decode() for x in values]

    @staticmethod
    def make_hash(target):
        if isinstance(target, str):
            target = target.encode()
        return hashlib.md5(target).hexdigest()

    def ping(self, name, location, **kwargs):
        self.connection.setex(name + "#" + self.make_hash(location),
                              self.ttl, location)
