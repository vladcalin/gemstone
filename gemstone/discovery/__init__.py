from .base import BaseDiscoveryStrategy
from .default import HttpDiscoveryStrategy
from .redis_strategy import RedisDiscoveryStrategy

from .cache import ServiceDiscoveryCache, DummyCache

__all__ = [
    'BaseDiscoveryStrategy',

    'HttpDiscoveryStrategy',
    'RedisDiscoveryStrategy',

    'ServiceDiscoveryCache',
    'DummyCache'
]
