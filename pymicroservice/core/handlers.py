import json
from functools import partial

from tornado.web import RequestHandler
from tornado.gen import coroutine


class TornadoJsonRpcHandler(RequestHandler):
    methods = None
    executor = None

    class _ErrorCodes:
        PARSE_ERROR = -32700
        INVALID_REQUEST = -32600
        METHOD_NOT_FOUND = -32601
        INVALID_PARAMS = -32602
        INTERNAL_ERROR = -32603
        OTHERS = -32000

    class _ErrorMessages:
        PARSE_ERROR = "Parse error"
        INVALID_REQUEST = "Invalid Request"
        METHOD_NOT_FOUND = "Method not found"
        INVALID_PARAMS = "Invalid params"
        INTERNAL_ERROR = "Internal error"

    # noinspection PyMethodOverriding
    def initialize(self, methods, executor):
        self.methods = methods
        self.executor = executor

    @coroutine
    def post(self):
        error = None
        result = None
        id_ = None

        # validate json structure
        try:
            req_body = json.loads(self.request.body.decode())
        except ValueError:
            error = self.make_error_object(self._ErrorCodes.PARSE_ERROR, self._ErrorMessages.PARSE_ERROR)
            self.write_response(None, error, None)
            return

        # validate keys
        if "method" not in req_body or "args" not in req_body:
            err = self.make_error_object(self._ErrorCodes.INVALID_REQUEST, self._ErrorMessages.INVALID_REQUEST)
            self.write_response(None, err, None)
            return

        if "id" not in req_body or req_body["id"] is None:
            self.write_response("received")

        # validate method name
        if req_body["method"] not in self.methods:
            err = self.make_error_object(self._ErrorCodes.METHOD_NOT_FOUND, self._ErrorMessages.METHOD_NOT_FOUND)
            self.write_response(error=err)
            return

        method = self.methods[req_body["method"]]
        method = self.prepare_method_call(method, req_body["args"])
        if not method:
            err = self.make_error_object(self._ErrorCodes.INVALID_REQUEST, self._ErrorMessages.INVALID_REQUEST)
            self.write_response(error=err)
            return
        result = yield self.call_method(method)

        self.write(self.make_response_dict(result, error, id_))

    def make_response_dict(self, result=None, error=None, id=None):
        response = {
            "result": result,
            "error": error,
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
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(self.make_response_dict(result, error, id)))

    def write_error(self, status_code, **kwargs):
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
        result = yield self.executor.submit(method)
        return result
