"""
Contains tests that assert the compliance with the
JSON RPC 2.0 specifications (http://www.jsonrpc.org/specification)
"""

import logging

import simplejson as json
import pytest

from tests.services.service_jsonrpc_specs import ServiceJsonRpcSpecs


@pytest.fixture
def app():
    return ServiceJsonRpcSpecs().make_tornado_app()


@pytest.mark.gen_test
def test_incomplete_json(http_client, base_url):
    body = json.dumps({"jsonrpc": "2.0", "method": "subtract"})[:15]
    result = yield http_client.fetch(base_url + "/api", method="POST", body=body,
                                     headers={"content-type": "application/json"})

    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["result"] is None
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["error"] == {"code": -32700, "message": "Parse error"}


# examples from http://www.jsonrpc.org/specification

@pytest.mark.gen_test
def test_rpc_call_with_positional_parameters(http_client, base_url):
    base_url += "/api"
    body = json.dumps({"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1})
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})

    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] == 19
    assert response_body["id"] == 1

    body = json.dumps({"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2})
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})

    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] == -19
    assert response_body["id"] == 2


@pytest.mark.gen_test
def test_rpc_call_with_named_parameters(http_client, base_url):
    base_url += "/api"
    body = json.dumps({"jsonrpc": "2.0", "method": "subtract", "params": {"a": 42, "b": 23}, "id": 3})
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] == 19
    assert response_body["id"] == 3

    body = json.dumps({"jsonrpc": "2.0", "method": "subtract", "params": {"b": 42, "a": 23}, "id": 4})
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] == -19
    assert response_body["id"] == 4


@pytest.mark.gen_test
def test_a_notification(http_client, base_url):
    base_url += "/api"
    body = json.dumps({"jsonrpc": "2.0", "method": "update", "params": {"a": 23}})
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] is None
    assert response_body["error"] is None


@pytest.mark.gen_test
def test_a_notification_inexistent_method(http_client, base_url):
    base_url += "/api"
    body = json.dumps({"jsonrpc": "2.0", "method": "does_not_exist", "params": {"a": 23}})
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] is None
    assert response_body["error"] is None


@pytest.mark.gen_test
def test_rpc_call_of_non_existent_method(http_client, base_url):
    base_url += "/api"
    body = json.dumps({"jsonrpc": "2.0", "method": "does_not_exist", "params": {"a": 23}, "id": 1})
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] is None
    assert response_body["error"] == {"code": -32601, "message": "Method not found"}
    assert response_body["id"] == 1


@pytest.mark.gen_test
def test_rpc_call_with_invalid_json(http_client, base_url):
    base_url += "/api"
    body = '{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]'
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})

    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] is None
    assert response_body["error"] == {"code": -32700, "message": "Parse error"}


@pytest.mark.gen_test
def test_rpc_call_with_invalid_request_object(http_client, base_url):
    base_url += "/api"
    body = json.dumps({"jsonrpc": "2.0", "method": "subtract", "params": "foobar"})
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] is None
    assert response_body["error"] == {"code": -32600, "message": "Invalid Request"}
    assert response_body["id"] is None


@pytest.mark.gen_test
def test_batch_call_with_invalid_json(http_client, base_url):
    base_url += "/api"
    body = '[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},{"jsonrpc": "2.0", "method"]'
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    print(response_body)
    assert isinstance(response_body, dict)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] is None
    assert response_body["error"] == {"code": -32700, "message": "Parse error"}


@pytest.mark.gen_test
def test_batch_call_empty_array(http_client, base_url):
    base_url += "/api"
    body = "[]"
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] is None
    assert response_body["error"] == {"code": -32600, "message": "Invalid Request"}
    assert response_body["id"] is None


@pytest.mark.gen_test
def test_batch_call_invalid_batch_but_not_empty(http_client, base_url):
    base_url += "/api"
    body = "[1]"
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    assert isinstance(response_body, list)
    assert len(response_body) == 1
    assert response_body[0]["jsonrpc"] == "2.0"
    assert response_body[0]["id"] is None
    assert response_body[0]["result"] is None
    assert response_body[0]["error"] == {"code": -32600, "message": "Invalid Request"}


@pytest.mark.gen_test
def test_batch_call_invalid_batch(http_client, base_url):
    base_url += "/api"
    body = "[1,2,3]"
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    assert isinstance(response_body, list)
    assert len(response_body) == 3

    for i in range(3):
        assert response_body[i]["jsonrpc"] == "2.0"
        assert response_body[i]["id"] is None
        assert response_body[i]["result"] is None
        assert response_body[i]["error"] == {"code": -32600, "message": "Invalid Request"}


@pytest.mark.gen_test
def test_batch_big_batch(http_client, base_url):
    base_url += "/api"
    body = [
        {"jsonrpc": "2.0", "method": "sum", "params": [1, 2, 4], "id": "1"},  # valid
        {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},  # notification
        {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": "2"},  # valid
        {"foo": "boo"},  # invalid request
        {"jsonrpc": "2.0", "method": "foo.get", "params": {"name": "myself"}, "id": "5"},  # method not found
        {"jsonrpc": "2.0", "method": "get_data", "id": "9"}  # valid no params
    ]
    expected_results = {
        "1": {"jsonrpc": "2.0", "result": 7, "id": "1", "error": None},
        "2": {"jsonrpc": "2.0", "result": 19, "id": "2", "error": None},
        "5": {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": "5", "result": None},
        "9": {"jsonrpc": "2.0", "result": ["hello", 5], "id": "9", "error": None}
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    assert isinstance(response_body, list)

    print(response_body)
    for request in body:
        req_id = request.get("id")
        if not req_id:
            continue

        expected = expected_results.get(req_id)
        actual_response = [x for x in response_body if x["id"] == req_id][0]

        assert expected == actual_response

# class JsonRpcSpecTestCase(AsyncHTTPTestCase):
#     def get_app(self):
#         app = ServiceJsonRpcSpecs().make_tornado_app()
#
#         # disable logging
#         hn = logging.NullHandler()
#         hn.setLevel(logging.DEBUG)
#         logging.getLogger("tornado.access").addHandler(hn)
#         logging.getLogger("tornado.access").propagate = False
#         return app
#
#     def test_invalid_json(self):
#         payload = {
#             "invalid": "no_data"
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#
#         self.assertEqual(resp["result"], None)
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["error"]["code"], -32600)
#         self.assertEqual(resp["error"]["message"].lower(), "invalid request")
#
#     def test_parse_error(self):
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"},
#                           body="{this_is_not_valid")
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["result"], None)
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["error"]["code"], -32700)
#         self.assertEqual(resp["error"]["message"].lower(), "parse error")
#
#     def test_bad_params_struct(self):
#         payload = {
#             "jsonrpc": "2.0",
#             "id": 7,
#             "method": "test_method_no_params",
#             "params": "just a string"
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["result"], None)
#         self.assertEqual(resp["id"], 7)
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["error"]["code"], -32600)
#         self.assertEqual(resp["error"]["message"].lower(), "invalid request")
#
#     def test_bad_parameters_names(self):
#         payload = {
#             "jsonrpc": "2.0",
#             "id": 8,
#             "method": "test_method_params",
#             "params": {
#                 "param_invalid_name": "invalid_name",
#                 "param1": "test"
#             }
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["result"], None)
#         self.assertEqual(resp["id"], 8)
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["error"]["code"], -32602)
#         self.assertEqual(resp["error"]["message"].lower(), "invalid params")
#
#     def test_bad_parameters_count(self):
#         payload = {
#             "jsonrpc": "2.0",
#             "id": 8,
#             "method": "test_method_params",
#             "params": {
#                 "param0": "invalid_name",
#                 "param1": "test",
#                 "param2": "test",
#                 "param3": "test",
#                 "param4": "test",
#                 "param5": "test"
#             }
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["result"], None)
#         self.assertEqual(resp["id"], 8)
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["error"]["code"], -32602)
#         self.assertEqual(resp["error"]["message"].lower(), "invalid params")
#
#     def test_bad_jsonrpc_version(self):
#         payload = {
#             "jsonrpc": "1.0",
#             "id": 33,
#             "method": "test_method_no_params"
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["result"], None)
#         self.assertIsNotNone(resp["error"])
#         self.assertEqual(resp["error"]["code"], -32600)
#         self.assertEqual(resp["error"]["message"].lower(), "invalid request")
#         self.assertEqual(resp["id"], 33)
#
#     def test_method_not_found(self):
#         payload = {
#             "jsonrpc": "2.0",
#             "id": 7,
#             "method": "method_does_not_exist",
#             "params": {
#                 "does": "not exist"
#             }
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["result"], None)
#         self.assertEqual(resp["id"], 7)
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["error"]["code"], -32601)
#         self.assertEqual(resp["error"]["message"].lower(), "method not found")
#
#     def test_bad_content_type(self):
#         payload = {
#             "jsonrpc": "2.0",
#             "id": 1,
#             "method": "test_method_params",
#             "params": {}
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/xxx-form-url-encoded"},
#                           body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["result"], None)
#         self.assertEqual(resp["error"]["code"], -32600)
#         self.assertEqual(resp["error"]["message"].lower(), "invalid request")
#
#     def test_bad_http_verb(self):
#         """
#         Handle this case
#
#         :return:
#         """
#         payload = {
#             "jsonrpc": "2.0",
#             "id": 7,
#             "method": "test_method_params",
#             "params": {}
#         }
#         resp = self.fetch("/api", method="PUT", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         self.assertEqual(resp.code, 405)
#
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["result"], None)
#         self.assertEqual(resp["error"]["message"].lower(), "method not allowed")
#
#     def test_notification(self):
#         payload = {
#             "jsonrpc": "2.0",
#             "id": None,
#             "method": "test_method_no_params",
#             "params": {}
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["result"], None)
#         self.assertEqual(resp["error"], None)
#         self.assertTrue("id" not in resp)
#
#     def test_notification_with_error(self):
#         """
#
#         :return:
#         """
#         payload = {
#             "jsonrpc": "2.0",
#             "id": None,
#             "method": "test_method_no_params",
#             "params": {
#                 "param_1": True
#             }
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["result"], None)
#         self.assertEqual(resp["error"], None)
#         self.assertTrue("id" not in resp)
#
#     def test_public_method_with_no_params(self):
#         payload = {
#             "jsonrpc": "2.0",
#             "id": 33,
#             "method": "test_method_no_params",
#             "params": {}
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["result"], "success_1")
#         self.assertEqual(resp["error"], None)
#         self.assertEqual(resp["id"], 33)
#
#     def test_public_method_with_no_params_field(self):
#         payload = {
#             "jsonrpc": "2.0",
#             "id": 37,
#             "method": "test_method_no_params"
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["result"], "success_1")
#         self.assertEqual(resp["error"], None)
#         self.assertEqual(resp["id"], 37)
#
#     def test_public_method_with_keyword_params(self):
#         payload = {
#             "jsonrpc": "2.0",
#             "id": 1,
#             "method": "test_method_params",
#             "params": {
#                 "param1": "test",
#                 "param2": "success"
#             }
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["result"], "this test is a success")
#         self.assertEqual(resp["error"], None)
#         self.assertEqual(resp["id"], 1)
#
#     def test_public_method_with_positional_params(self):
#         payload = {
#             "jsonrpc": "2.0",
#             "id": 1,
#             "method": "test_method_params",
#             "params": ["test", "success"]
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["result"], "this test is a success")
#         self.assertEqual(resp["error"], None)
#         self.assertEqual(resp["id"], 1)
#
#     def test_public_method_with_variable_params(self):
#         payload = {
#             "jsonrpc": "2.0",
#             "id": 1,
#             "method": "test_method_var_params",
#             "params": {
#                 "param1": "test",
#                 "param2": "success",
#                 "param3": 3,
#                 "param4": False
#             }
#         }
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#         self.assertEqual(resp["jsonrpc"], "2.0")
#         self.assertEqual(resp["result"], {"kwargs": {
#             "param1": "test",
#             "param2": "success",
#             "param3": 3,
#             "param4": False
#         }})
#         self.assertEqual(resp["error"], None)
#
#     def _get_response_by_id(self, batch_response, id_):
#         filtered = [x for x in batch_response if x.get("id", None) == id_]
#         if not filtered:
#             return None
#         else:
#             return filtered[0]
#
#     def test_batch_req_resp(self):
#
#         payload = [
#             {"jsonrpc": "2.0", "id": 1, "method": "test_method_no_params", "params": {}},
#             {"jsonrpc": "2.0", "id": 2, "method": "test_method_params",
#              "params": {"param1": "test", "param2": "test2"}},
#             {"jsonrpc": "2.0", "id": 3, "method": "test_method_no_params", "params": {}}
#         ]
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"},
#                           body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#
#         response_id_1 = self._get_response_by_id(resp, 1)
#         self.assertEqual(response_id_1["jsonrpc"], "2.0")
#         self.assertEqual(response_id_1["error"], None)
#         self.assertEqual(response_id_1["result"], "success_1")
#
#         response_id_2 = self._get_response_by_id(resp, 2)
#         self.assertEqual(response_id_2["jsonrpc"], "2.0")
#         self.assertEqual(response_id_2["error"], None)
#         self.assertEqual(response_id_2["result"], "this test is a test2")
#
#         response_id_3 = self._get_response_by_id(resp, 3)
#         self.assertEqual(response_id_3["jsonrpc"], "2.0")
#         self.assertEqual(response_id_3["error"], None)
#         self.assertEqual(response_id_3["result"], "success_1")
#
#     def test_batch_bad_request_parse_error(self):
#         payload = [
#             {"jsonrpc": "2.0", "id": 1, "method": "test_method_no_params", "params": {}},
#             {"jsonrpc": "2.0", "id": 2, "method": "test_method_params",
#              "params": {"param1": "test", "param2": "test2"}},
#             {"jsonrpc": "2.0", "id": 3, "method": "test_method_no_params", "params": {}}
#         ]
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"},
#                           body=json.dumps(payload)[:-10])
#         resp = json.loads(resp.body.decode())
#
#         self.assertEqual(resp["result"], None)
#         self.assertEqual(resp["error"]["code"], -32700)
#         self.assertEqual(resp["error"]["message"].lower(), "parse error")
#
#     def test_batch_one_bad_request(self):
#         payload = [
#             {"jsonrpc": "2.0", "id": 1, "method": "method_not_found", "params": {}},
#             {"jsonrpc": "2.0", "id": 2, "method": "test_method_params",
#              "params": {"param1": "test", "param2": "test2"}},
#             {"jsonrpc": "2.0", "id": 3, "method": "test_method_no_params", "params": {}}
#         ]
#         resp = self.fetch("/api", method="POST", headers={"Content-Type": "application/json"},
#                           body=json.dumps(payload))
#         resp = json.loads(resp.body.decode())
#
#         response_id_1 = self._get_response_by_id(resp, 1)
#         self.assertEqual(response_id_1["jsonrpc"], "2.0")
#         self.assertEqual(response_id_1["error"]["code"], -32601)
#         self.assertEqual(response_id_1["error"]["message"].lower(), "method not found")
#         self.assertEqual(response_id_1["result"], None)
#
#         response_id_2 = self._get_response_by_id(resp, 2)
#         self.assertEqual(response_id_2["jsonrpc"], "2.0")
#         self.assertEqual(response_id_2["error"], None)
#         self.assertEqual(response_id_2["result"], "this test is a test2")
#
#         response_id_3 = self._get_response_by_id(resp, 3)
#         self.assertEqual(response_id_3["jsonrpc"], "2.0")
#         self.assertEqual(response_id_3["error"], None)
#         self.assertEqual(response_id_3["result"], "success_1")
