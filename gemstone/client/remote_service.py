import os
import urllib.request
import asyncio
import random
import threading
import string

from concurrent.futures import ThreadPoolExecutor
import simplejson as json

from gemstone.errors import CalledServiceError


class CallableMethod(object):
    def __init__(self, remote_service, method, req_id):
        self.url = remote_service.url
        self.service = remote_service
        self.method = method
        self.req_id = req_id

    def __call__(self, *args, **kwargs):
        __async = kwargs.pop("__async", False)

        if kwargs and args:
            raise ValueError(
                "Cannot have positional arguments and keyword arguments at the same time")

        if __async:
            return AsyncMethodCall(self.service, self.method, args, kwargs)

        # construct the "params" value
        params = args or kwargs

        # construct the request headers
        request_headers = {"Content-Type": "application/json"}

        options = self.service.options
        request_body = {}

        if options:
            if options.get("auth_type") == "header":
                request_headers[options.get("auth_params", "X-Api-Token")] = options.get(
                    "auth_token")
            elif options.get("auth_type") == "cookie":
                request_headers["cookie"] = "{}={}".format(options.get("auth_params", "AuthCookie"),
                                                           options.get("auth_token"))
            elif options.get("auth_type") == "request":
                request_body.setdefault(options.get("auth_params", "auth_token"),
                                        options.get("auth_token"))

        # construct the request body
        request_body.setdefault("jsonrpc", "2.0")
        request_body.setdefault("method", self.method)
        request_body.setdefault("params", params)

        if self.req_id:
            request_body["id"] = self.req_id
        response = self.service.make_request_sync(self.url, json_body=request_body,
                                                  headers=request_headers)

        if not self.req_id:
            return  # it is a notification and we do not care about the response

        response = json.loads(response)
        if response["error"]:
            raise CalledServiceError(response["error"])
        return response["result"]


class AsyncMethodCall(object):
    def __init__(self, service, method, args, kwargs):
        """
        Encapsulates an asynchronous method call. The user should not be instantiated by the user.

        The instantiation of this class triggers a http request in the background.

        :param service: a :py:class:`gemstone.RemoteService` instance that is properly initialized
        :param method: a :py:class:`str` instance with the name if the method to be called
        :param args: a list with the arguments
        :param kwargs: a `dict` with the keyword arguments

        .. versionadded:: 0.5.0
        """
        self.service = service
        self.method = method
        self.args = args
        self.kwargs = kwargs

        self._lock = threading.Lock()
        self._result = None
        self._error = None
        self._finished = False

        self._background_thread = threading.Thread(target=self._make_sync_call)
        self._background_thread.daemon = True
        self._background_thread.start()

    def _make_sync_call(self):
        error = None
        try:
            result = getattr(self.service.methods, self.method)(*self.args, **self.kwargs)
        except CalledServiceError as e:
            error = e.args[0]
            result = None

        with self._lock:
            self._finished = True
            self._error = error
            self._result = result

    def wait(self):
        """
        Waits for the async call to finish and returns the result

        :return: the result of the method call
        """
        self._background_thread.join()
        return self._result

    def result(self):
        """
        Returns the result of the method call or `None` if not available or the call failed.
        """
        with self._lock:
            return self._result

    def error(self):
        """
        Returns the error from the method call (if any).
        """
        with self._lock:
            return self._error

    def finished(self):
        """
        Indicates if the request was finished or not.
        """
        with self._lock:
            return self._finished

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<AsyncMethodCall service={} method={} id={}>".format(self.service, self.method,
                                                                     hash(self))


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
                                  None if self._is_notification else self._remote_service.get_new_id())
        else:
            return super(ServiceMethodProxy, self).__getattribute__(item)


class RemoteService(object):
    def __init__(self, url, *, threads=os.cpu_count(), options=None):
        """
        Class used to interact with other services.

        Quick examples:

        - calling a method for result: ``x = service.methods.method_to_call(args)``
        - calling a method as a notification: ``service.notifications.method_to_call(args)``
        - calling a method for result asynchronously:
          ``r = service.methods.method_to_call(args, __async=True); r.wait()``

        :param url: The endpoint where the service listens. Must be a valid
                    URL (ex: ``"http://127.0.0.1:5000/api"``)
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

    def get_new_id(self):
        return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    @property
    def methods(self):
        """
        Returns a proxy object through which you can call remote methods. Usage:

        ::

            client = gemstone.RemoteService(service_url)
            print(client.methods.say_hello("world"))
            # hello world

        For asynchronous call, you must pass the ``__async=True`` parameter to the method call

        ::

            async_resp = client.methods.say_hello("world", __async=True)
            async_resp.wait()
            print(async_resp.result())
            # hello world

        """
        return self._method_proxy

    @property
    def notifications(self):
        """
        Same as :py:meth:`gemstone.RemoteService.methods` but does not wait for a response.
        Returns ``None`` immediately.
        """
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
        Returns a list of string representing the method names exposed by the service
        and updates the internal state of the object to reflect the returned state
        of the service.
        """
        res = self.make_request_sync(self.url,
                                     json_body={"jsonrpc": "2.0", "method": "get_service_specs",
                                                "id": self.req_id},
                                     headers={"Content-Type": "application/json"})
        res = json.loads(res)
        self.req_id += 1
        self.name = res["result"]["name"]
        self._methods = list(res["result"]["methods"].keys())
        return res

    def get_available_methods(self):
        """
        Returns a list with all the available methods exposed by the remote service.

        :return: a :py:class:`list` with :py:class:`str` representing the names of the
                 exposed methods
        """
        return self._methods

    @classmethod
    def get_service_by_name(cls, registry_url, name_pattern, choose_algorithm="random"):
        """
        Queries a service registry for the connection details (host and port) given a
        glob name pattern.

        .. versionadded:: 0.1.4

        :param registry_url: A string representing the url where the service registry is
                             accessible at.
                             Example: "http://192.168.0.1/api"
        :param name_pattern: A glob name pattern for which to return the available services.
                             For example: "otherservice", "otherservice.worker*",
                             "otherservice.worker.0?"
        :param choose_algorithm: A string representing how the service should be picked
                                 if multiples services are returned. Choices are:
                                 'random' (choosing at random)
        :return: a :py:class:`gemstone.RemoteService` instance through which to interact
                 with the service
        """
        choose_algs = {
            "random": lambda l: random.choice(l)
        }
        if choose_algorithm not in choose_algs.keys():
            raise ValueError(
                "Invalid choosing algorithm: '{}'. Valid choices are {}".format(choose_algorithm,
                                                                                choose_algs.keys()))

        registry = RemoteService(registry_url)
        service_locations = registry.methods.locate_service(name_pattern)
        if not service_locations:
            raise CalledServiceError("Unable to locate service {}".format(name_pattern))

        service_specs = choose_algs[choose_algorithm](service_locations)

        url = service_specs
        return RemoteService(url)
