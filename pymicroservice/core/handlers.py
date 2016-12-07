import json
from functools import partial
import asyncio

from tornado.web import RequestHandler
from tornado.gen import coroutine

__all__ = [
    'TornadoJsonRpcHandler'
]

class TornadoJsonRpcHandler(RequestHandler):
    methods = None
    executor = None
    api_token_header = None
    api_token_handler = None

    class _GenericErrorId:
        PARSE_ERROR = "PARSE_ERROR"
        INVALID_REQUEST = "INVALID_REQUEST"
        METHOD_NOT_FOUND = "METHOD_NOT_FOUND"
        INVALID_PARAMS = "INVALID_PARAMS"
        INTERNAL_ERROR = "INTERNAL_ERROR"
        ACCESS_DENIED = "ACCESS_DENIED"

        ALL = [PARSE_ERROR, INVALID_PARAMS, METHOD_NOT_FOUND, INVALID_REQUEST, INTERNAL_ERROR, ACCESS_DENIED]

    class _ErrorCodes:
        PARSE_ERROR = -32700
        INVALID_REQUEST = -32600
        METHOD_NOT_FOUND = -32601
        INVALID_PARAMS = -32602
        INTERNAL_ERROR = -32603
        OTHERS = -32000
        ACCESS_DENIED = -32001

    class _ErrorMessages:
        PARSE_ERROR = "Parse error"
        INVALID_REQUEST = "Invalid Request"
        METHOD_NOT_FOUND = "Method not found"
        INVALID_PARAMS = "Invalid params"
        INTERNAL_ERROR = "Internal error"
        ACCESS_DENIED = "Access denied"

    # noinspection PyMethodOverriding
    def initialize(self, methods, executor, api_token_header, api_token_handler):
        self.methods = methods
        self.executor = executor
        self.api_token_header = api_token_header
        self.api_token_handler = api_token_handler

    @coroutine
    def post(self):
        if self.request.headers.get("Content-type") != "application/json":
            error = self.get_generic_jsonrpc_response(self._GenericErrorId.INVALID_REQUEST)
            self.write_response(None, error, None)
            return

        # validate json structure
        try:
            req_body = json.loads(self.request.body.decode())
        except ValueError:
            error = self.get_generic_jsonrpc_response(self._GenericErrorId.PARSE_ERROR)
            self.write_response(None, error, None)
            return

        if isinstance(req_body, dict):
            result = yield self.handle_single_request(req_body)
            if result is None:  # is notification and a ack resp was already sent
                return
            self.write_response(result=result["result"], error=result["error"],
                                id=result.get("id", None))  # ID not returned if some error appeared
        elif isinstance(req_body, list):
            results = yield self.handle_batch_request(req_body)
            valid_results = list(filter(lambda x: x is not None, results))
            self.write_batch_response(*valid_results)
        else:
            self.write_response(error=self.get_generic_jsonrpc_response(self._GenericErrorId.INVALID_REQUEST))

    @coroutine
    def handle_single_request(self, single_request):
        """
        Handles a single request object and returns the correct result as follows:

        - A valid response object if it is a regular request (with ID)
        - ``None`` if it was a notification (if None is returned, a response object with "received" body
          was already sent to the client.

        :param single_request: A :py:class:`dict` object representing a Request object
        :return: A :py:class:`dict` object representing a Response object or None

        """
        is_notification = False
        error = None
        result = None
        id_ = single_request.get("id", None)

        # validate keys
        if not self.validate_jsonrpc_structure(single_request):
            err = self.get_generic_jsonrpc_response(self._GenericErrorId.INVALID_REQUEST)
            return self.make_response_dict(None, err, id_)

        # check if it is a notification or the client waits a response
        if "id" not in single_request or single_request["id"] is None:
            self.write_response("received")
            is_notification = True

        # validate method name
        if single_request["method"] not in self.methods:
            if not is_notification:
                err = self.get_generic_jsonrpc_response(self._GenericErrorId.METHOD_NOT_FOUND)
                return self.make_response_dict(error=err, id=id_)

        # check for private access
        method = self.methods[single_request["method"]]
        if method.is_private:
            if not self.api_token_handler(self.request.headers.get(self.api_token_header, None)):
                err = self.get_generic_jsonrpc_response(self._GenericErrorId.ACCESS_DENIED)
                return self.make_response_dict(error=err, id=id_)

        method = self.prepare_method_call(method, single_request.get("params", {}))
        if not method:
            if not is_notification:
                err = self.get_generic_jsonrpc_response(self._GenericErrorId.INVALID_REQUEST)
                return self.make_response_dict(error=err, id=id_)
            return
        try:
            result = yield self.call_method(method)
        except Exception as e:
            err = self.get_generic_jsonrpc_response(self._GenericErrorId.INTERNAL_ERROR)
            err["data"] = {
                "class": type(e).__name__,
                "info": str(e)
            }
            return self.make_response_dict(None, err, id_)

        if not is_notification:
            return self.make_response_dict(result, error, id_)

    def get_generic_jsonrpc_response(self, error_id):
        if error_id not in self._GenericErrorId.ALL:
            raise ValueError("Invalid error id: {0} (allowed only {1})".format(error_id, self._GenericErrorId.ALL))

        return self.make_error_object(
            getattr(self._ErrorCodes, error_id),
            getattr(self._ErrorMessages, error_id)
        )

    def validate_jsonrpc_structure(self, body):
        """
        Makes sure the **body** contains the right keys in order to
        respect the JSON RPC specifications. The request must contain: ``"jsonrpc"`` key with the ``"2.0"`` value,
        a ``"method"`` key.

        :param body: :py:class:`dict` representing a JSON RPC request
        :return:
        """
        for mandatory_key in ["jsonrpc", "method"]:
            if mandatory_key not in body:
                return False

        if body["jsonrpc"] != "2.0":
            return False

        return True

    def make_response_dict(self, result=None, error=None, id=None):
        response = {
            "jsonrpc": "2.0",
            "result": result,
            "error": error
        }

        if id:
            response["id"] = id
        return response

    def make_error_object(self, code, message, data=None):
        err_obj = {
            "code": code,
            "message": message,
        }
        if data:
            err_obj["data"] = data
        return err_obj

    def write_response(self, result=None, error=None, id=None):
        """
        Writes a json rpc response ``{"result": result, "error": error, "id": id}``.
        If the ``id`` is ``None``, the response will not contain an ``id`` field.
        The response is sent to the client as an ``application/json`` response.

        :param result: :py:class:`dict` representing the method call result, ``None`` if an error occurred.
        :param error: :py:class:`dict` representing the error resulted in the method call, ``None`` if no error occurred
        :param id: the ``id`` of the request that generated this response
        :return:
        """
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(self.make_response_dict(result, error, id)))

    def write_batch_response(self, *results):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(results))

    def write_error(self, status_code, **kwargs):
        if status_code == 405:
            self.set_status(405)
            self.write_response(None, {"message": "Method not allowed"})
            return

        exc_info = kwargs["exc_info"]
        err = self.make_error_object(self._ErrorCodes.INTERNAL_ERROR, self._ErrorMessages.INTERNAL_ERROR, data={
            "class": str(exc_info[0].__name__),
            "info": str(exc_info[1])
        })
        self.set_status(200)
        self.write_response(error=err)

    def prepare_method_call(self, method, args):
        if isinstance(args, list):
            to_call = partial(method, *args)
        elif isinstance(args, dict):
            to_call = partial(method, **args)
        else:
            return None
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
    def handle_batch_request(self, req_body):
        responses = yield [self.handle_single_request(single_req) for single_req in req_body]
        return responses
