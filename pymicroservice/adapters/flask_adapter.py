import logging
import inspect
import functools

from flask import Flask, jsonify, request

from pymicroservice.adapters.base import BaseAdapter

__all__ = [
    'FlaskAdapter'
]


class FlaskAdapter(BaseAdapter):
    def __init__(self, host, port, api_root="/"):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.api_root = api_root
        self.doc = {}

    def register_endpoint(self, endpoint):
        name = endpoint.__name__
        parameters = inspect.getargspec(endpoint)

        endpoint = self._wrap_endpoint(endpoint)
        self.app.route(self.api_root.rstrip("/") + "/" + name, methods=["post"])(endpoint)
        self.doc[self.api_root.rstrip("/") + "/" + name] = {
            "description": endpoint.__doc__ or "",
            "parameters": parameters
        }

    def _wrap_endpoint(self, endpoint):
        @functools.wraps(endpoint)
        def wrapper(*args, **kwargs):
            args_, kwargs_ = self.extract_args(*args, **kwargs)
            result = endpoint(*args_, **kwargs_)
            self.extract_args()
            return result

        return wrapper

    def serve(self):
        self._register_help()

        self.app.run(self.host, self.port)

    def _register_help(self):
        def return_help():
            return jsonify(self.doc)

        self.app.route(self.api_root.rstrip("/") + "/", methods=["get"])(return_help)
        # pass

    def extract_args(self, *args, **kwargs):
        post_data = self._extract_post_data()
        to_return = dict(post_data)
        for k, v in to_return.items():
            print(k, v)
            if isinstance(v, list) and len(v) == 1:
                to_return[k] = v[0]
        return (), to_return

    def _extract_post_data(self):
        post_data = request.form
        return post_data
