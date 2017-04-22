import urllib.request
import os

from multiprocessing.pool import ThreadPool
import simplejson as json

from gemstone.client.structs import MethodCall, Notification, Result, BatchResult, AsyncMethodCall
from gemstone.errors import CalledServiceError


class RemoteService(object):
    RESPONSE_CODES = {
        -32001: "access_denied",
        -32603: "internal_error",
        -32601: "method_not_found",
        -32602: "invalid_params"
    }

    def __init__(self, service_endpoint, *, authentication_method=None):
        self.url = service_endpoint
        self.authentication_method = authentication_method
        self._thread_pool = None

    def _get_thread_pool(self):
        # lazily initialized
        if not self._thread_pool:
            self._thread_pool = ThreadPool(os.cpu_count())
        return self._thread_pool

    def handle_single_request(self, request_object):
        """
        Handles a single request object and returns the raw response

        :param request_object:
        """
        if not isinstance(request_object, (MethodCall, Notification)):
            raise TypeError("Invalid type for request_object")

        method_name = request_object.method_name
        params = request_object.params
        req_id = request_object.id

        request_body = self.build_request_body(method_name, params, id=req_id)
        http_request = self.build_http_request_obj(request_body)

        try:
            response = urllib.request.urlopen(http_request)
        except urllib.request.HTTPError as e:
            raise CalledServiceError(e)

        if not req_id:
            return

        response_body = json.loads(response.read().decode())
        return response_body

    def build_request_body(self, method_name, params, id=None):
        request_body = {
            "jsonrpc": "2.0",
            "method": method_name,
            "params": params

        }
        if id:
            request_body['id'] = id
        return request_body

    def build_http_request_obj(self, request_body):
        request = urllib.request.Request(self.url)
        request.add_header("Content-Type", "application/json")
        request.add_header("User-Agent", "gemstone-client")
        request.data = json.dumps(request_body).encode()
        request.method = "POST"
        return request

    def call_method(self, method_name_or_object, params=None):
        """
        Calls the ``method_name`` method from the given service and returns a
        :py:class:`gemstone.client.structs.Result` instance.

        :param method_name_or_object: The name of te called method or a ``MethodCall`` instance
        :param params: A list of dict representing the parameters for the request
        :return: a :py:class:`gemstone.client.structs.Result` instance.
        """
        if isinstance(method_name_or_object, MethodCall):
            req_obj = method_name_or_object
        else:
            req_obj = MethodCall(method_name_or_object, params)
        raw_response = self.handle_single_request(req_obj)
        response_obj = Result(result=raw_response["result"], error=raw_response['error'],
                              id=raw_response["id"], method_call=req_obj)
        return response_obj

    def call_method_async(self, method_name_or_object, params=None):
        """
        Calls the ``method_name`` method from the given service asynchronously
        and returns a :py:class:`gemstone.client.structs.AsyncMethodCall` instance.

        :param method_name_or_object: The name of te called method or a ``MethodCall`` instance
        :param params: A list of dict representing the parameters for the request
        :return: a :py:class:`gemstone.client.structs.AsyncMethodCall` instance.
        """
        thread_pool = self._get_thread_pool()

        if isinstance(method_name_or_object, MethodCall):
            req_obj = method_name_or_object
        else:
            req_obj = MethodCall(method_name_or_object, params)

        async_result_mp = thread_pool.apply_async(self.handle_single_request, args=(req_obj,))
        return AsyncMethodCall(req_obj=req_obj, async_resp_object=async_result_mp)

    def notify(self, method_name_or_object, params=None):
        """
        Sends a notification to the service by calling the ``method_name``
        method with the ``params`` parameters. Does not wait for a response, even
        if the response triggers an error.

        :param method_name_or_object: the name of the method to be called or a ``Notification``
                                      instance
        :param params: a list of dict representing the parameters for the call
        :return: None
        """
        if isinstance(method_name_or_object, Notification):
            req_obj = method_name_or_object
        else:
            req_obj = Notification(method_name_or_object, params)
        self.handle_single_request(req_obj)

    def call_batch(self, *requests):
        body = []
        ids = {}
        for item in requests:
            if not isinstance(item, (MethodCall, Notification)):
                raise TypeError("Invalid type for batch item: {}".format(item))

            body.append(self.build_request_body(
                method_name=item.method_name,
                params=item.params or {},
                id=item.id
            ))
            if isinstance(item, MethodCall):
                ids[body[-1]["id"]] = item

        results = self.handle_batch_request(body)

        batch_result = BatchResult()
        for result in results:
            result_obj = Result(result["result"], result["error"], result["id"],
                                method_call=ids[result["id"]])
            batch_result.add_response(result_obj)
        return batch_result

    def handle_batch_request(self, body):
        request = self.build_http_request_obj(body)

        try:
            response = urllib.request.urlopen(request)
        except urllib.request.HTTPError as e:
            raise CalledServiceError(e)

        resp_body = json.loads(response.read().decode())
        return resp_body
