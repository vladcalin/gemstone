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
    service = ServiceJsonRpcSpecs()
    service._initial_setup()
    return service.make_tornado_app()


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
    body = json.dumps(
        {"jsonrpc": "2.0", "method": "subtract", "params": {"a": 42, "b": 23}, "id": 3})
    result = yield http_client.fetch(base_url, method="POST", body=body,
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    response_body = json.loads(result.body)
    assert response_body["jsonrpc"] == "2.0"
    assert response_body["result"] == 19
    assert response_body["id"] == 3

    body = json.dumps(
        {"jsonrpc": "2.0", "method": "subtract", "params": {"b": 42, "a": 23}, "id": 4})
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
        {"jsonrpc": "2.0", "method": "foo.get", "params": {"name": "myself"}, "id": "5"},
        # method not found
        {"jsonrpc": "2.0", "method": "get_data", "id": "9"}  # valid no params
    ]
    expected_results = {
        "1": {"jsonrpc": "2.0", "result": 7, "id": "1", "error": None},
        "2": {"jsonrpc": "2.0", "result": 19, "id": "2", "error": None},
        "5": {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": "5",
              "result": None},
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
