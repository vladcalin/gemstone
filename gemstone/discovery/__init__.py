from .base import BaseDiscoveryStrategy
from .default import HttpDiscoveryStrategy
from .redis_strategy import RedisDiscoveryStrategy

__all__ = [
    'BaseDiscoveryStrategy',

    'HttpDiscoveryStrategy',
    'RedisDiscoveryStrategy'
]
