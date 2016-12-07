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
            request_headers.setdefault(self.service.api_header or "X-Api-Token", self.service.api_key)

        # construct the request body
        request_body = {
            "jsonrpc": "2.0",
            "method": self.method,
            "params": params,
        }
        if self.req_id:
            request_body["id"] = self.req_id

        response = self.service.make_request_sync(self.url, json_body=request_body, headers=request_headers)

        if not self.req_id:
            return  # it is a notification and we do not care about the response

        response = json.loads(response)
        if response["error"]:
            raise CalledServiceError(response["error"])

        return response["result"]


class ServiceMethodProxy(object):
    def __init__(self, methods, remote_service, is_notification=False):
        self._methods = methods
        self._remote_service = remote_service
        self._is_notification = is_notification

    def __getattribute__(self, item):
        if item.startswith("_"):
            return super(ServiceMethodProxy, self).__getattribute__(item)
        if item in self._methods:

            return CallableMethod(self._remote_service, item,
                                  None if self._is_notification else self._remote_service.req_id)
        else:
            return super(ServiceMethodProxy, self).__getattribute__(item)


class RemoteService(object):
    def __init__(self, url, *, threads=os.cpu_count(), api_key=None, api_header=None):
        """
        Class used to interact with other services

        :param url: The endpoint where the service listens. Must be a valid URL (ex: ``"http://127.0.0.1:5000/api"``)
        :param threads:
        :param api_key: The api key to be used for requests
        :param api_header: The custom api header that is used by the service
        """
        self.url = url
        self._executor = ThreadPoolExecutor(threads)
        self.req_id = 1
        self.api_key = api_key
        self.api_header = api_header

        self._methods = []
        self.name = None
        self.get_services_info()

        self._method_proxy = ServiceMethodProxy(self._methods, self)
        self._notification_proxy = ServiceMethodProxy(self._methods, self, is_notification=True)

    @property
    def methods(self):
        return self._method_proxy

    @property
    def notifications(self):
        return self._notification_proxy

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
        """
        Returns a list with all the available methods exposed by the remote service.

        :return: a :py:class:`list` with :py:class:`str` representing the names of the exposed methods
        """
        return self._methods
