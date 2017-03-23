from tornado.testing import AsyncHTTPTestCase
import simplejson as json

import pytest

from tests.services.service_microservice import TestService


@pytest.fixture
def app():
    service = TestService()
    service.skip_configuration = True
    service._initial_setup()
    return service.make_tornado_app()


@pytest.mark.gen_test
def test_simple_call_no_parameters(http_client, base_url):
    base_url += "/api"
    body = {
        "id": 1,
        "method": "say_hello",
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)

    assert resp_body["id"] == 1
    assert resp_body["error"] is None
    assert resp_body["result"] == "hello"
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_simple_call_positional_arguments(http_client, base_url):
    base_url += "/api"
    body = {
        "id": 1,
        "method": "subtract",
        "params": [10, 20],
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)

    assert resp_body["id"] == 1
    assert resp_body["error"] is None
    assert resp_body["result"] == -10
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_simple_call_keyword_arguments(http_client, base_url):
    base_url += "/api"
    body = {
        "id": 1,
        "method": "subtract",
        "params": {"b": 20, "a": 10},
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)

    assert resp_body["id"] == 1
    assert resp_body["error"] is None
    assert resp_body["result"] == -10
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_simple_call_variable_length_positional_arguments(http_client, base_url):
    base_url += "/api"
    body = {
        "id": 1,
        "method": "sum",
        "params": list(range(0, 100)),
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)

    assert resp_body["id"] == 1
    assert resp_body["error"] is None
    assert resp_body["result"] == 4950
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_simple_call_raise_exception(http_client, base_url):
    base_url += "/api"
    body = {
        "id": 1,
        "method": "divide",
        "params": {"a": 10, "b": 0},
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)

    assert resp_body["id"] == 1
    assert resp_body["result"] is None
    assert resp_body["error"] is not None
    assert resp_body["error"]["code"] == -32603
    assert resp_body["error"]["message"] == "Internal error"
    assert resp_body["error"]["data"]["class"] == "ZeroDivisionError"
    assert resp_body["error"]["data"]["info"] == "division by zero"
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_simple_call_wrong_arguments_too_few_positional_arguments(http_client, base_url):
    base_url += "/api"
    body = {
        "id": 1,
        "method": "subtract",
        "params": [10],
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert resp_body["id"] == 1
    assert resp_body["result"] is None
    assert resp_body["error"] is not None
    assert resp_body["error"]["code"] == -32602
    assert resp_body["error"]["message"] == "Invalid params"
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_simple_call_wrong_arguments_too_many_positional_arguments(http_client, base_url):
    base_url += "/api"
    body = {
        "id": 1,
        "method": "subtract",
        "params": [10, 20, 30],
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert resp_body["id"] == 1
    assert resp_body["result"] is None
    assert resp_body["error"] is not None
    assert resp_body["error"]["code"] == -32602
    assert resp_body["error"]["message"] == "Invalid params"
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_simple_call_wrong_arguments_too_few_keyword_arguments(http_client, base_url):
    base_url += "/api"
    body = {
        "id": 1,
        "method": "subtract",
        "params": {"a": 10},
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert resp_body["id"] == 1
    assert resp_body["result"] is None
    assert resp_body["error"] is not None
    assert resp_body["error"]["code"] == -32602
    assert resp_body["error"]["message"] == "Invalid params"
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_simple_call_wrong_arguments_too_many_keyword_arguments(http_client, base_url):
    base_url += "/api"
    body = {
        "id": 1,
        "method": "subtract",
        "params": {"a": 10, "b": 20, "c": 30},
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert resp_body["id"] == 1
    assert resp_body["result"] is None
    assert resp_body["error"] is not None
    assert resp_body["error"]["code"] == -32602
    assert resp_body["error"]["message"] == "Invalid params"
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_simple_call_wrong_arguments_no_arguments(http_client, base_url):
    base_url += "/api"
    body = {
        "id": 1,
        "method": "subtract",
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert resp_body["id"] == 1
    assert resp_body["result"] is None
    assert resp_body["error"] is not None
    assert resp_body["error"]["code"] == -32602
    assert resp_body["error"]["message"] == "Invalid params"
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_notification_valid(http_client, base_url):
    base_url += "/api"
    body = {
        "method": "subtract",
        "params": [20, 10],
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert "id" not in resp_body
    assert resp_body["result"] is None
    assert resp_body["error"] is None
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_notification_method_not_found(http_client, base_url):
    base_url += "/api"
    body = {
        "method": "foobar",
        "params": [20, 10],
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert "id" not in resp_body
    assert resp_body["result"] is None
    assert resp_body["error"] is None
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_notification_invalid_params(http_client, base_url):
    base_url += "/api"
    body = {
        "method": "divide",
        "params": [20, 10, 30],
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert "id" not in resp_body
    assert resp_body["result"] is None
    assert resp_body["error"] is None
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_notification_internal_error(http_client, base_url):
    base_url += "/api"
    body = {
        "method": "divide",
        "params": [20, 0],
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert "id" not in resp_body
    assert resp_body["result"] is None
    assert resp_body["error"] is None
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_private_call_wrong_token(http_client, base_url):
    base_url += "/api"
    body = {
        "id": 3,
        "method": "private_sum",
        "params": [13, -13],
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json",
                                              "X-Testing-Token": "bad_token"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert resp_body["id"] == 3
    assert resp_body["result"] is None
    assert resp_body["error"] is not None
    assert resp_body["error"]["code"] == -32001
    assert resp_body["error"]["message"] == "Access denied"
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_private_call_wrong_token_and_wrong_parameters(http_client, base_url):
    # without a valid token, somebody should not be able to get information
    # about certain methods, such as the parameters
    base_url += "/api"
    body = {
        "id": 3,
        "method": "private_sum",
        "params": [13],
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json",
                                              "X-Testing-Token": "bad_token"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert resp_body["id"] == 3
    assert resp_body["result"] is None
    assert resp_body["error"] is not None
    assert resp_body["error"]["code"] == -32001
    assert resp_body["error"]["message"] == "Access denied"
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_private_call_ok_token(http_client, base_url):
    # without a valid token, somebody should not be able to get information
    # about certain methods, such as the parameters
    base_url += "/api"
    body = {
        "id": 3,
        "method": "private_sum",
        "params": [13, -13],
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json",
                                              "X-Testing-Token": "testing_token"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert resp_body["id"] == 3
    assert resp_body["result"] == 0
    assert resp_body["error"] is None
    assert resp_body["jsonrpc"] == "2.0"


@pytest.mark.gen_test
def test_private_call_ok_token_wrong_parameters(http_client, base_url):
    # without a valid token, somebody should not be able to get information
    # about certain methods, such as the parameters
    base_url += "/api"
    body = {
        "id": 3,
        "method": "private_sum",
        "params": [13],
        "jsonrpc": "2.0"
    }

    result = yield http_client.fetch(base_url, method="POST", body=json.dumps(body),
                                     headers={"content-type": "application/json",
                                              "X-Testing-Token": "testing_token"})
    assert result.code == 200
    resp_body = json.loads(result.body)
    print(resp_body)
    assert resp_body["id"] == 3
    assert resp_body["result"] is None
    assert resp_body["error"] is not None
    assert resp_body["error"]["code"] == -32602
    assert resp_body["error"]["message"] == "Invalid params"
    assert resp_body["jsonrpc"] == "2.0"
