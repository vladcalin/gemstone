import os
import urllib.request
import asyncio
import random
import threading
import string

from concurrent.futures import ThreadPoolExecutor
import simplejson as json

from gemstone.client.structs import MethodCall, Notification, Result, BatchResult
from gemstone.core.structs import GenericResponse
from gemstone.errors import CalledServiceError, MethodNotFoundError, AccessDeniedError, \
    InternalErrorError, InvalidParamsError, UnknownError


class RemoteService(object):
    RESPONSE_CODES = {
        GenericResponse.ACCESS_DENIED.error["code"]: "access_denied",
        GenericResponse.INTERNAL_ERROR.error["code"]: "internal_error",
        GenericResponse.METHOD_NOT_FOUND.error["code"]: "method_not_found",
        GenericResponse.INVALID_PARAMS.error["code"]: "invalid_params"
    }

    def __init__(self, service_endpoint, *, authentication_method=None):
        self.url = service_endpoint
        self.authentication_method = authentication_method

    def handle_single_request(self, request_object):
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

        if response_body["result"] is not None:
            return response_body["result"]
        else:
            # there was an error
            error_code = response_body["error"]["code"]
            error_type = self.RESPONSE_CODES.get(error_code, "unknown")

            self.raise_for_type(error_type, method_name=method_name, params=params)

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

    def call_method(self, method_name, params=None):
        req_obj = MethodCall(method_name, params)
        raw_response = self.handle_single_request(req_obj)
        response_obj = Result(result=raw_response["result"], error=raw_response['error'],
                              id=raw_response["id"], method_call=req_obj)
        return response_obj

    def call_method_async(self, method_name, params=None):
        pass

    def notify(self, method_name, params):
        req_obj = Notification(method_name, params)
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

    def raise_for_type(self, error_type, method_name, params):
        if error_type == "method_not_found":
            raise MethodNotFoundError("Method '{}' not found".format(method_name))
        elif error_type == "invalid_params":
            raise InvalidParamsError(
                "Invalid parameters for method '{}': {}".format(method_name, params))
        elif error_type == "access_denied":
            raise AccessDeniedError("Not authorized to call '{}'".format(method_name))
        elif error_type == "internal_error":
            raise InternalErrorError("An internal error occurred")

        raise UnknownError("An unknown error has occurred")

    def handle_batch_request(self, body):
        request = self.build_http_request_obj(body)

        try:
            response = urllib.request.urlopen(request)
        except urllib.request.HTTPError as e:
            raise CalledServiceError(e)

        resp_body = json.loads(response.read().decode())
        return resp_body


if __name__ == '__main__':
    service = RemoteService("http://localhost:8000/api")
    result = service.call_batch(
        MethodCall("slow_method", [1]),
        MethodCall("slow_method", [2]),
        MethodCall("slow_method", [3]),
    )
    for x in result:
        print(x)
