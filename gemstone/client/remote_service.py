import os
import urllib.request
import json
import asyncio
import random

from concurrent.futures import ThreadPoolExecutor

from gemstone.errors import CalledServiceError


class CallableMethod(object):
    def __init__(self, remote_service, method, req_id):
        self.url = remote_service.url
        self.service = remote_service
        self.method = method
        self.req_id = req_id

    def __call__(self, *args, **kwargs):
        if kwargs and args:
            raise ValueError("Cannot have positional arguments and keyword arguments at the same time")

        # construct the "params" value
        params = args or kwargs

        # construct the request headers
        request_headers = {"Content-Type": "application/json"}

        options = self.service.options
        request_body = {}

        if options:
            if options.get("auth_type") == "header":
                request_headers[options.get("auth_params", "X-Api-Token")] = options.get("auth_token")
            elif options.get("auth_type") == "cookie":
                request_headers["cookie"] = "{}={}".format(options.get("auth_params", "AuthCookie"),
                                                           options.get("auth_token"))
            elif options.get("auth_type") == "request":
                request_body.setdefault(options.get("auth_params", "auth_token"), options.get("auth_token"))

        # construct the request body
        request_body.setdefault("jsonrpc", "2.0")
        request_body.setdefault("method", self.method)
        request_body.setdefault("params", params)

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
    def __init__(self, remote_service, is_notification=False):
        self._methods = remote_service._methods
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
    def __init__(self, url, *, threads=os.cpu_count(), options=None):
        """
        Class used to interact with other services

        :param url: The endpoint where the service listens. Must be a valid URL (ex: ``"http://127.0.0.1:5000/api"``)
        :param threads:
        :param options: a :py:class:`dict` with options for the client. Available options are:
                        - auth_type: 'cookie', 'header', 'request'
                        - auth_params: depends on auth_type.
                        - auth_token: :py:class`str` with
        """
        self.url = url
        self._executor = ThreadPoolExecutor(threads)
        self.req_id = 1
        self.options = options

        self._methods = []
        self.name = None
        self.refresh_service_info()

        self._method_proxy = ServiceMethodProxy(self)
        self._notification_proxy = ServiceMethodProxy(self, is_notification=True)

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

    def refresh_service_info(self):
        """
        Returns a list of string representing the method names exposed by the service and updates the internal state
        of the object to reflect the returned state of the service.
        """
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

    @classmethod
    def get_service_by_name(cls, registry_url, name_pattern, choose_algorithm="random"):
        """
        Queries a service registry for the connection details (host and port) given a glob name pattern.

        .. versionadded:: 0.1.4

        :param registry_url: A string representing the url where the service registry is accessible at.
                             Example: "http://192.168.0.1/api"
        :param name_pattern: A glob name pattern for which to return the available services. For
                             example: "otherservice", "otherservice.worker*", "otherservice.worker.0?"
        :param choose_algorithm: A string representing how the service should be picked if multiples services are
                                 returned. Choices are: 'random' (choosing at random)
        :return: a :py:class:`gemstone.RemoteService` instance through which to interact with the service
        """
        choose_algs = {
            "random": lambda l: random.choice(l)
        }
        if choose_algorithm not in choose_algs.keys():
            raise ValueError(
                "Invalid choosing algorithm: '{}'. Valid choices are {}".format(choose_algorithm, choose_algs.keys()))

        registry = RemoteService(registry_url)
        service_locations = registry.methods.locate_service(name_pattern)
        if not service_locations:
            raise CalledServiceError("Unable to locate service {}".format(name_pattern))

        service_specs = choose_algs[choose_algorithm](service_locations)

        url = service_specs
        return RemoteService(url)
