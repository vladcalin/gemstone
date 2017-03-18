import os
import urllib.request
import asyncio
import random
import threading
import string

from concurrent.futures import ThreadPoolExecutor
import simplejson as json

from gemstone.core.structs import GenericResponse
from gemstone.errors import CalledServiceError, MethodNotFoundError, AccessDeniedError, \
    InternalErrorError, InvalidParamsError, UnknownError


class AsyncMethodCall(object):
    def __init__(self):
        pass

    def is_ready(self):
        pass

    def result(self):
        pass

    def get(self):
        pass

    def successful(self):
        pass

    def reraise(self):
        pass


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

    def call_method(self, method_name, params=None):
        if not params:
            params = {}

        request_body = {
            "jsonrpc": "2.0",
            "method": method_name,
            "params": params,
            "id": self.get_request_id()
        }

        request = self.build_request_obj(request_body)

        try:
            response = urllib.request.urlopen(request)
        except urllib.request.HTTPError as e:
            raise CalledServiceError(e)

        response_body = json.loads(response.read().decode())

        if response_body["result"] is not None:
            return response_body["result"]
        else:
            # there was an error
            error_code = response_body["error"]["code"]
            error_type = self.RESPONSE_CODES.get(error_code, "unknown")

            self.raise_for_type(error_type, method_name=method_name, params=params)

    def build_request_obj(self, request_body):
        request = urllib.request.Request(self.url)
        request.add_header("Content-Type", "application/json")
        request.add_header("User-Agent", "gemstone-client")
        request.data = json.dumps(request_body).encode()
        request.method = "POST"
        return request

    def call_method_async(self, method_name, params=None):
        pass

    def notify(self, method_name, params):
        pass

    def prepare_batch(self, *requests):
        pass

    @staticmethod
    def get_request_id():
        return "".join([random.choice(string.ascii_letters) for _ in range(10)])

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


if __name__ == '__main__':
    service = RemoteService("http://nuc01.local:8000/api")

    result = service.call_method("get_service_specs")
    print(result)
