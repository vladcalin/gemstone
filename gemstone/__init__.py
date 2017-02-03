"""
Build microservices with Python
"""

from gemstone.core.microservice import MicroService
from gemstone.core.decorators import private_api_method, public_method
from gemstone.core.handlers import TornadoJsonRpcHandler
from gemstone.client.remote_service import RemoteService

from gemstone.util import as_completed, first_completed, make_callbacks

__author__ = "Vlad Calin"
__email__ = "vlad.s.calin@gmail.com"

__version__ = "0.4.0"
