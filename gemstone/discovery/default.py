import random
import string

from tornado.httpclient import HTTPClient, HTTPRequest
import simplejson as json

from gemstone.discovery.base import BaseDiscoveryStrategy


class HttpDiscoveryStrategy(BaseDiscoveryStrategy):
    """
    A discovery strategy that uses the HTTP protocol as transport. Each ``ping`` and ``locate``
    calls translate to HTTP requests.

    """
    def __init__(self, registry_location):
        self.registry = registry_location

    def make_jsonrpc_call(self, url, method, params):
        client = HTTPClient()
        body = json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": "".join([random.choice(string.ascii_letters) for _ in range(10)])
        })

        request = HTTPRequest(url, method="POST", headers={"content-type": "application/json"},
                              body=body)
        result = client.fetch(request)
        return result

    def ping(self, name, location, **kwargs):
        self.make_jsonrpc_call(self.registry, "ping",
                               {"name": name, "url": location})

    def locate(self, name):
        response = self.make_jsonrpc_call(self.registry, "locate_service", {"name": name})
        resp_as_dict = json.loads(response.body.decode())
        return resp_as_dict["result"]
