import logging
import inspect
import functools

from flask import Flask, jsonify, request

from pymicroservice.adapters.base import BaseAdapter

__all__ = [
    'FlaskAdapter'
]


class FlaskAdapter(BaseAdapter):
    """

    Usage:

    Each method will be processed so that it can be called via

    POST /api
    {
        "method": "say_hello",
        "args": {
            "name": "world"
        }
    }

    {
        "success": true,
        "result": "hello world",
        "error": null
    }

    """

    def __init__(self, host, port, api_root="/"):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.api_root = api_root
        self.doc = {"methods": {}}
        self.endpoints = {}

    def register_endpoint(self, endpoint):
        name = endpoint.__name__
        param_sig = self._generate_argument_signature(endpoint)

        self.endpoints[name] = endpoint
        self.doc["methods"][name] = {
            "description": endpoint.__doc__ or "",
            "parameters": param_sig
        }

    def _generate_argument_signature(self, endpoint):
        parameters = inspect.getargspec(endpoint)
        param_sig = ", ".join(parameters[0][1:])
        if parameters[1]:
            param_sig += ", *" + parameters[1]
        if parameters[2]:
            param_sig += ", **" + parameters[2]
        return param_sig

    def handle_request(self):
        req_json = request.json
        method_name = req_json.get("method")
        args = req_json.get("args")
        if not method_name:
            raise KeyError("Missing 'method_name' field from request body")
        if not args:
            raise KeyError("Missing 'args' field from request body")

        endpoint = self.endpoints.get(method_name)
        if not endpoint:
            raise KeyError("Method not found")

        result = self.endpoints[method_name](**args)
        return self.make_result(to_return=result)

    def serve(self):
        self._register_help()
        self.init_handle_error()

        self.app.route(self.api_root.rstrip("/") + "/api", methods=["post"])(self.handle_request)
        self.app.run(self.host, self.port)

    def _register_help(self):
        def return_help():
            return jsonify(self.doc)

        self.app.route(self.api_root.rstrip("/") + "/api", methods=["get"])(return_help)

    def init_handle_error(self):
        self.app.errorhandler(Exception)(self.handle_error)

    def handle_error(self, *args, **kwargs):
        exc_instance = args[0]
        return self.make_result(None, error=str(exc_instance))

    def make_result(self, to_return, error=None):
        return jsonify({
            "error": error,
            "success": error is None,
            "result": to_return
        })
