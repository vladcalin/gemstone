from functools import partial
import copy

import simplejson as json
from tornado.web import RequestHandler
from tornado.gen import coroutine

from gemstone.core.structs import JsonRpcResponse, JsonRpcRequest, JsonRpcRequestBatch, JsonRpcResponseBatch, \
    GenericResponse, parse_json_structure, JsonRpcParseError, JsonRpcInvalidRequestError

__all__ = [
    'TornadoJsonRpcHandler',
    'GemstoneCustomHandler'
]


# noinspection PyAbstractClass
class GemstoneCustomHandler(RequestHandler):
    """
    Base class for custom Tornado handlers that
    can be added to the microservice.

    Offers a reference to the microservice through the ``self.microservice`` attribute.

    """

    def __init__(self, *args, **kwargs):
        #: reference to the microservice that uses the request handler
        self.microservice = None
        super(GemstoneCustomHandler, self).__init__(*args, **kwargs)

    # noinspection PyMethodOverriding
    def initialize(self, microservice):
        self.microservice = microservice


# noinspection PyAbstractClass
class TornadoJsonRpcHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        self.response_is_sent = False
        self.methods = None
        self.executor = None
        self.validation_strategies = None
        self.api_token_handlers = None
        self.logger = None
        self.microservice = None
        super(TornadoJsonRpcHandler, self).__init__(*args, **kwargs)

    # noinspection PyMethodOverriding
    def initialize(self, microservice):
        self.logger = microservice.logger
        self.methods = microservice.methods
        self.executor = microservice._executor
        self.validation_strategies = microservice.validation_strategies
        self.api_token_handlers = microservice.api_token_is_valid
        self.response_is_sent = False
        self.microservice = microservice

    @coroutine
    def post(self):
        if self.request.headers.get("Content-type") != "application/json":
            self.write_single_response(GenericResponse.INVALID_REQUEST)
            return

        req_body_raw = self.request.body.decode()
        try:
            req_object = json.loads(req_body_raw)
        except json.JSONDecodeError:
            self.write_single_response(GenericResponse.PARSE_ERROR)
            return

        # handle the actual call
        if isinstance(req_object, dict):
            # single call
            try:
                req_object = JsonRpcRequest.from_dict(req_object)
            except JsonRpcInvalidRequestError:
                self.write_single_response(GenericResponse.INVALID_REQUEST)

            if req_object.is_notification():
                self.write_single_response(GenericResponse.NOTIFICATION_RESPONSE)

            result = yield self.handle_single_request(req_object)
            self.write_single_response(result)
        elif isinstance(req_object, list):
            if len(req_object) == 0:
                self.write_single_response(GenericResponse.INVALID_REQUEST)
                return

            # batch call
            invalid_requests = []
            requests_futures = []
            notification_futures = []

            for item in req_object:
                try:
                    if not isinstance(item, dict):
                        raise JsonRpcInvalidRequestError()
                    current_rpc_call = JsonRpcRequest.from_dict(item)

                    # handle notifications
                    if current_rpc_call.is_notification():
                        # we trigger their execution, but we don't yield for their results
                        notification_futures.append(self.handle_single_request(current_rpc_call))
                    else:
                        requests_futures.append(self.handle_single_request(current_rpc_call))
                except JsonRpcInvalidRequestError:
                    invalid_requests.append(GenericResponse.INVALID_REQUEST)

            finished_rpc_calls = yield requests_futures
            self.write_batch_response(JsonRpcResponseBatch(invalid_requests + finished_rpc_calls))
        else:
            self.write_single_response(GenericResponse.INVALID_REQUEST)

    @coroutine
    def handle_single_request(self, request_object):
        """
        Handles a single request object and returns the correct result as follows:

        - A valid response object if it is a regular request (with ID)
        - ``None`` if it was a notification (if None is returned, a response object with "received" body
          was already sent to the client.

        :param request_object: A :py:class:`gemstone.core.structs.JsonRpcRequest` object representing a Request object
        :return: A :py:class:`gemstone.core.structs.JsonRpcResponse` object representing a Response object or
                 None if no response is expected (it was a notification)

        """
        # dont handle responses?
        if isinstance(request_object, JsonRpcResponse):
            return request_object

        error = None
        result = None
        id_ = request_object.id

        # validate method name
        if request_object.method not in self.methods:
            resp = GenericResponse.METHOD_NOT_FOUND
            resp.id = id_
            return resp

        # check for private access
        method = self.methods[request_object.method]
        if method.is_private:
            token = self.extract_api_token()
            if not self.api_token_handlers(token):
                resp = GenericResponse.ACCESS_DENIED
                resp.id = id_
                return resp

        method = self.prepare_method_call(method, request_object.params)

        # before request hook
        request_object_copy = copy.deepcopy(request_object)
        self.microservice.before_method_call(request_object_copy)

        try:
            result = yield self.call_method(method)
        except TypeError as e:
            # TODO: find a proper way to check that the function got the wrong parameters (with **kwargs)
            if "got an unexpected keyword argument" in e.args[0]:
                resp = GenericResponse.INVALID_PARAMS
                resp.id = id_
                return resp
            # TODO: find a proper way to check that the function got the wrong parameters (with *args)
            elif "takes" in e.args[0] and "positional argument" in e.args[0] and "were given" in e.args[0]:
                resp = GenericResponse.INVALID_PARAMS
                resp.id = id_
                return resp
            else:
                raise
        except Exception as e:
            err = GenericResponse.INTERNAL_ERROR
            err.id = id_
            err.error["data"] = {
                "class": type(e).__name__,
                "info": str(e)
            }
            return err

        to_return_resp = JsonRpcResponse(result=result, error=error, id=id_)

        self.microservice.after_method_call(request_object_copy, to_return_resp)

        return to_return_resp

    def write_single_response(self, response_obj):
        """
        Writes a json rpc response ``{"result": result, "error": error, "id": id}``.
        If the ``id`` is ``None``, the response will not contain an ``id`` field.
        The response is sent to the client as an ``application/json`` response. Only one call per
        response is allowed

        :param response_obj: A Json rpc response object
        :return:
        """
        if not isinstance(response_obj, JsonRpcResponse):
            raise ValueError("Expected JsonRpcResponse, but got {} instead".format(type(response_obj).__name__))

        if not self.response_is_sent:
            self.set_status(200)
            self.set_header("Content-Type", "application/json")
            self.finish(response_obj.to_string())
            self.response_is_sent = True

    def write_batch_response(self, batch_response):
        self.set_header("Content-Type", "application/json")
        self.write(batch_response.to_string())

    def write_error(self, status_code, **kwargs):
        if status_code == 405:
            self.set_status(405)
            self.write_single_response(JsonRpcResponse(error={"code": 405, "message": "Method not allowed"}))
            return

        exc_info = kwargs["exc_info"]
        err = GenericResponse.INTERNAL_ERROR
        err.error["data"] = {
            "class": str(exc_info[0].__name__),
            "info": str(exc_info[1])
        }
        self.set_status(200)
        self.write_single_response(err)

    def prepare_method_call(self, method, args):
        """
        Wraps a method so that method() will call ``method(*args)`` or ``method(**args)``, depending of args type

        :param method: a callable object (method)
        :param args: dict or list with the parameters for the function
        :return: a 'patched' callable
        """
        if isinstance(args, list):
            to_call = partial(method, *args)
        elif isinstance(args, dict):
            to_call = partial(method, **args)
        else:
            raise TypeError("args must be list or dict but got {} instead".format(type(args).__name__))
        return to_call

    @coroutine
    def call_method(self, method):
        """
        Calls a blocking method in an executor, in order to preserve the non-blocking behaviour

        :param method: The method to be called (with no arguments).
        :return: the result of the method call
        """
        result = yield self.executor.submit(method)
        return result

    @coroutine
    def handle_batch_request(self, batch_req_obj):
        responses = yield [self.handle_single_request(single_req) for single_req in batch_req_obj.iter_items()]
        return responses

    def extract_api_token(self):
        for handler in self.validation_strategies:
            token = handler.extract_api_token(self)
            if token:
                return token
