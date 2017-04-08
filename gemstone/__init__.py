"""
Build microservices with Python
"""

from gemstone.core.microservice import MicroService
from gemstone.core.decorators import event_handler, exposed_method
from gemstone.core.handlers import TornadoJsonRpcHandler, GemstoneCustomHandler
from gemstone.core.container import Container

from gemstone.util import as_completed, first_completed

__author__ = "Vlad Calin"
__email__ = "vlad.s.calin@gmail.com"

__version__ = "0.11.0"

__all__ = [
    # core classes
    'MicroService',

    'Container',

    # decorators
    'event_handler',
    'exposed_method',

    # tornado handler
    'TornadoJsonRpcHandler',
    'GemstoneCustomHandler',

    # async utilities
    'as_completed',
    'first_completed'
]
