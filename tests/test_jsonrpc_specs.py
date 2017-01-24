import json
import logging

from tornado.testing import AsyncHTTPTestCase, gen_test

from gemstone import MicroService, public_method, private_api_method


class TestService(MicroService):
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

    def test_bad_params_struct(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "test_method_no_params",
            "params": "just a string"
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["id"], 7)
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["error"]["code"], -32600)
        self.assertEqual(resp["error"]["message"].lower(), "invalid request")

    def test_bad_parameters_names(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "test_method_params",
            "params": {
                "param_invalid_name": "invalid_name",
                "param1": "test"
            }
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["id"], 8)
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["error"]["code"], -32602)
        self.assertEqual(resp["error"]["message"].lower(), "invalid params")

    def test_bad_parameters_count(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "test_method_params",
            "params": {
                "param0": "invalid_name",
                "param1": "test",
                "param2": "test",
                "param3": "test",
                "param4": "test",
                "param5": "test"
            }
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["id"], 8)
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["error"]["code"], -32602)
        self.assertEqual(resp["error"]["message"].lower(), "invalid params")

    def test_bad_jsonrpc_version(self):
        payload = {
            "jsonrpc": "1.0",
            "id": 33,
            "method": "test_method_no_params"
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], None)
        self.assertIsNotNone(resp["error"])
        self.assertEqual(resp["error"]["code"], -32600)
        self.assertEqual(resp["error"]["message"].lower(), "invalid request")
        self.assertEqual(resp["id"], 33)

    def test_method_not_found(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "method_does_not_exist",
            "params": {
                "does": "not exist"
            }
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["id"], 7)
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["error"]["code"], -32601)
        self.assertEqual(resp["error"]["message"].lower(), "method not found")

    def test_bad_content_type(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test_method_params",
            "params": {}
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
            "id": 7,
            "method": "test_method_params",
            "params": {}
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
            "params": {}
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["error"], None)
        self.assertTrue("id" not in resp)

    def test_notification_with_error(self):
        """

        :return:
        """
        payload = {
            "jsonrpc": "2.0",
            "id": None,
            "method": "test_method_no_params",
            "params": {
                "param_1": True
            }
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["error"], None)
        self.assertTrue("id" not in resp)

    def test_public_method_with_no_params(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 33,
            "method": "test_method_no_params",
            "params": {}
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], "success_1")
        self.assertEqual(resp["error"], None)
        self.assertEqual(resp["id"], 33)

    def test_public_method_with_no_params_field(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 37,
            "method": "test_method_no_params"
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], "success_1")
        self.assertEqual(resp["error"], None)
        self.assertEqual(resp["id"], 37)

    def test_public_method_with_keyword_params(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test_method_params",
            "params": {
                "param1": "test",
                "param2": "success"
            }
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], "this test is a success")
        self.assertEqual(resp["error"], None)
        self.assertEqual(resp["id"], 1)

    def test_public_method_with_positional_params(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test_method_params",
            "params": ["test", "success"]
        }
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["result"], "this test is a success")
        self.assertEqual(resp["error"], None)
        self.assertEqual(resp["id"], 1)

    def test_public_method_with_variable_params(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test_method_var_params",
            "params": {
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

    def _get_response_by_id(self, batch_response, id_):
        filtered = [x for x in batch_response if x.get("id", None) == id_]
        if not filtered:
            return None
        else:
            return filtered[0]

    def test_batch_req_resp(self):

        payload = [
            {"jsonrpc": "2.0", "id": 1, "method": "test_method_no_params", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "test_method_params",
             "params": {"param1": "test", "param2": "test2"}},
            {"jsonrpc": "2.0", "id": 3, "method": "test_method_no_params", "params": {}}
        ]
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
        resp = json.loads(resp.body.decode())

        response_id_1 = self._get_response_by_id(resp, 1)
        self.assertEqual(response_id_1["jsonrpc"], "2.0")
        self.assertEqual(response_id_1["error"], None)
        self.assertEqual(response_id_1["result"], "success_1")

        response_id_2 = self._get_response_by_id(resp, 2)
        self.assertEqual(response_id_2["jsonrpc"], "2.0")
        self.assertEqual(response_id_2["error"], None)
        self.assertEqual(response_id_2["result"], "this test is a test2")

        response_id_3 = self._get_response_by_id(resp, 3)
        self.assertEqual(response_id_3["jsonrpc"], "2.0")
        self.assertEqual(response_id_3["error"], None)
        self.assertEqual(response_id_3["result"], "success_1")

    def test_batch_bad_request_parse_error(self):
        payload = [
            {"jsonrpc": "2.0", "id": 1, "method": "test_method_no_params", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "test_method_params",
             "params": {"param1": "test", "param2": "test2"}},
            {"jsonrpc": "2.0", "id": 3, "method": "test_method_no_params", "params": {}}
        ]
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"},
                          body=json.dumps(payload)[:-10])
        resp = json.loads(resp.body.decode())

        self.assertEqual(resp["result"], None)
        self.assertEqual(resp["error"]["code"], -32700)
        self.assertEqual(resp["error"]["message"].lower(), "parse error")

    def test_batch_one_bad_request(self):
        payload = [
            {"jsonrpc": "2.0", "id": 1, "method": "method_not_found", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "test_method_params",
             "params": {"param1": "test", "param2": "test2"}},
            {"jsonrpc": "2.0", "id": 3, "method": "test_method_no_params", "params": {}}
        ]
        resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"},
                          body=json.dumps(payload))
        resp = json.loads(resp.body.decode())

        response_id_1 = self._get_response_by_id(resp, 1)
        self.assertEqual(response_id_1["jsonrpc"], "2.0")
        self.assertEqual(response_id_1["error"]["code"], -32601)
        self.assertEqual(response_id_1["error"]["message"].lower(), "method not found")
        self.assertEqual(response_id_1["result"], None)

        response_id_2 = self._get_response_by_id(resp, 2)
        self.assertEqual(response_id_2["jsonrpc"], "2.0")
        self.assertEqual(response_id_2["error"], None)
        self.assertEqual(response_id_2["result"], "this test is a test2")

        response_id_3 = self._get_response_by_id(resp, 3)
        self.assertEqual(response_id_3["jsonrpc"], "2.0")
        self.assertEqual(response_id_3["error"], None)
        self.assertEqual(response_id_3["result"], "success_1")
