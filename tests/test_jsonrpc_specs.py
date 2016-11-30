import json
import logging

from tornado.testing import AsyncHTTPTestCase, gen_test

from pymicroservice import PyMicroService, public_method, private_api_method


class TestService(PyMicroService):
    name = "test.service"

    host = "127.0.0.1"
    port = 9999

    @public_method
    def test_method_no_params(self):
        return "success_1"

    @public_method
    def test_method_params(self, param1, param2):
        return "this {} is a {}".format(param1, param2)

    @public_method
    def test_method_var_params(self, **kwargs):
        return {
            "kwargs": kwargs
        }

    @private_api_method
    def test_method_priv_no_params(self):
        pass

    def api_token_is_valid(self, api_token):
        return api_token == "test-token"


class JsonRpcSpecTestCase(AsyncHTTPTestCase):
    def get_app(self):
        app = TestService().make_tornado_app()

        # disable logging
        hn = logging.NullHandler()
        hn.setLevel(logging.DEBUG)
        logging.getLogger("tornado.access").addHandler(hn)
        logging.getLogger("tornado.access").propagate = False
        return app

    def test_invalid_json(self):
        payload = {
            "invalid": "no_data"
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())

        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["error"]["code"], -32600)
        self.assertEqual(resp["error"]["message"].lower(), "invalid request")

    def test_parse_error(self):
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"},
                          body="{this_is_not_valid")
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["error"]["code"], -32700)
        self.assertEqual(resp["error"]["message"].lower(), "parse error")

    def test_method_not_found(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "method_does_not_exist",
            "args": {
                "does": "not exist"
            }
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["error"]["code"], -32601)
        self.assertEqual(resp["error"]["message"].lower(), "method not found")

    def test_bad_content_type(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test_method_params",
            "args": {}
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/xxx-form-url-encoded"},
                          body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["error"]["code"], -32600)
        self.assertEqual(resp["error"]["message"].lower(), "invalid request")

    def test_bad_http_verb(self):
        """
        Handle this case

        :return:
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test_method_params",
            "args": {}
        }
        resp = self.fetch("/api", method="PUT", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        self.assertEqual(resp.code, 405)

        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["error"]["message"].lower(), "method not allowed")

    def test_notification(self):
        payload = {
            "jsonrpc": "2.0",
            "id": None,
            "method": "test_method_no_params",
            "args": {}
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], "received")
        self.assertEqual(resp["error"], None)

    def test_public_method_with_no_params(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test_method_no_params",
            "args": {}
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], "success_1")
        self.assertEqual(resp["error"], None)

    def test_public_method_with_params(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test_method_params",
            "args": {
                "param1": "test",
                "param2": "success"
            }
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], "this test is a success")
        self.assertEqual(resp["error"], None)

    def test_public_method_with_variable_params(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test_method_var_params",
            "args": {
                "param1": "test",
                "param2": "success",
                "param3": 3,
                "param4": False
            }
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], {"kwargs": {
            "param1": "test",
            "param2": "success",
            "param3": 3,
            "param4": False
        }})
        self.assertEqual(resp["error"], None)
