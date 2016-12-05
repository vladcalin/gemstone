import os
import urllib.request
import json
import asyncio

from concurrent.futures import ThreadPoolExecutor

from pymicroservice.errors import CalledServiceError


class CallableMethod(object):
    def __init__(self, service_instance, method, req_id):
        self.url = service_instance.url
        self.service = service_instance
        self.method = method
        self.req_id = req_id

    def __call__(self, *args, **kwargs):
        if kwargs and args:
            raise ValueError("Cannot have positional arguments and keyword arguments at the same time")

        # construct the "params" value
        params = args or kwargs

        # construct the request headers
        request_headers = {"Content-Type": "application/json"}
        if self.service.api_key:
            request_headers.setdefault("X-Api-Token", self.service.api_key)

        response = self.service.make_request_sync(self.url, json_body={
            "jsonrpc": "2.0",
            "method": self.method,
            "params": params,
            "id": self.req_id
        }, headers=request_headers)
        response = json.loads(response)
        if response["error"]:
            raise CalledServiceError(response["error"])

        return response["result"]


class ServiceMethodProxy(object):
    def __init__(self, methods, remote_service):
        self._methods = methods
        self._remote_service = remote_service

    def __getattribute__(self, item):
        if item.startswith("_"):
            return super(ServiceMethodProxy, self).__getattribute__(item)
        if item in self._methods:

            return CallableMethod(self._remote_service, item, self._remote_service.req_id)
        else:
            return super(ServiceMethodProxy, self).__getattribute__(item)


class RemoteService(object):
    def __init__(self, url, threads=os.cpu_count(), api_key=None):
        self.url = url
        self._executor = ThreadPoolExecutor(threads)
        self.req_id = 1
        self.api_key = api_key

        self._methods = []
        self.name = None
        self.get_services_info()

        self._method_proxy = ServiceMethodProxy(self._methods, self)

    @property
    def methods(self):
        return self._method_proxy

    def make_request_sync(self, url, json_body=None, headers=None):
        request = urllib.request.Request(url)

        if json_body:
            if isinstance(json_body, dict):
                json_body = json.dumps(json_body)
            request.data = json_body.encode()
            request.method = "POST"
        else:
            request.method = "GET"

        if headers:
            for k, v in headers.items():
                request.add_header(k, v)

        response = urllib.request.urlopen(request)
        return response.read().decode()

    def get_services_info(self):
        res = self.make_request_sync(self.url,
                                     json_body={"jsonrpc": "2.0", "method": "get_service_specs", "id": self.req_id},
                                     headers={"Content-Type": "application/json"})
        res = json.loads(res)
        self.req_id += 1
        self.name = res["result"]["name"]
        self._methods = list(res["result"]["methods"].keys())
        return res

    def get_available_methods(self):
        return self._methods
