import pytest

from gemstone.core.structs import JsonRpcParseError, JsonRpcInvalidRequestError, JsonRpcRequest, \
    JsonRpcResponse, JsonRpcRequestBatch, JsonRpcResponseBatch


def test_jsonrpc_request_from_dict_ok():
    # complete
    jsonrpc_dict = {
        "jsonrpc": "2.0",
        "method": "test",
        "params": {"test": "ok"},
        "id": 1
    }
    obj = JsonRpcRequest.from_dict(jsonrpc_dict)

    assert obj.method == "test"
    assert obj.id == 1
    assert obj.params == {"test": "ok"}

    # positional params
    jsonrpc_dict = {
        "jsonrpc": "2.0",
        "method": "test",
        "params": [1, 2, 3, 4, 5],
        "id": 1
    }
    obj = JsonRpcRequest.from_dict(jsonrpc_dict)

    assert obj.method == "test"
    assert obj.id == 1
    assert obj.params == [1, 2, 3, 4, 5]

    # without params
    jsonrpc_dict = {
        "jsonrpc": "2.0",
        "method": "test",
        "id": 1
    }
    obj = JsonRpcRequest.from_dict(jsonrpc_dict)

    assert obj.method == "test"
    assert obj.id == 1
    assert obj.params == {}

    # without id
    jsonrpc_dict = {
        "jsonrpc": "2.0",
        "method": "test",
        "params": {"test": "ok"},
    }
    obj = JsonRpcRequest.from_dict(jsonrpc_dict)

    assert obj.method == "test"
    assert obj.id is None
    assert obj.params == {"test": "ok"}


def test_jsonrpc_request_from_string_ok():
    json1 = '{"jsonrpc": "2.0","method": "test","params": {"test": "ok"},"id": 1}'
    json2 = '{"jsonrpc": "2.0","method": "test","params": [1,2,3,4,5],"id": 1}'
    json3 = '{"jsonrpc": "2.0","method": "test","id": 1}'
    json4 = '{"jsonrpc": "2.0","method": "test","params": {"test": "ok"}}'

    json1_obj = JsonRpcRequest.from_string(json1)
    assert json1_obj.method == "test"
    assert json1_obj.id == 1
    assert json1_obj.params == {"test": "ok"}

    json2_obj = JsonRpcRequest.from_string(json2)
    assert json2_obj.method == "test"
    assert json2_obj.id == 1
    assert json2_obj.params == [1, 2, 3, 4, 5]

    json3_obj = JsonRpcRequest.from_string(json3)
    assert json3_obj.method == "test"
    assert json3_obj.id == 1
    assert json3_obj.params == {}

    json4_obj = JsonRpcRequest.from_string(json4)
    assert json4_obj.method == "test"
    assert json4_obj.id is None
    assert json4_obj.params == {"test": "ok"}


def test_jsonrpc_request_from_dict_fail():
    # no protocol version
    jsonrpc_dict = {
        "method": "test",
        "params": {"test": "ok"},
        "id": 1
    }

    with pytest.raises(JsonRpcInvalidRequestError):
        JsonRpcRequest.from_dict(jsonrpc_dict)

    # no method
    jsonrpc_dict = {
        "jsonrpc": "2.0",
        "params": {"test": "ok"},
        "id": 1
    }

    with pytest.raises(JsonRpcInvalidRequestError):
        JsonRpcRequest.from_dict(jsonrpc_dict)

    # wrong params type (string)
    jsonrpc_dict = {
        "jsonrpc": "2.0",
        "method": "test",
        "params": "wrong",
        "id": 1
    }

    with pytest.raises(JsonRpcInvalidRequestError):
        JsonRpcRequest.from_dict(jsonrpc_dict)

    # wrong params type (bool)
    jsonrpc_dict = {
        "jsonrpc": "2.0",
        "method": "test",
        "params": True,
        "id": 1
    }

    with pytest.raises(JsonRpcInvalidRequestError):
        JsonRpcRequest.from_dict(jsonrpc_dict)

    # wrong id type (bool)
    jsonrpc_dict = {
        "jsonrpc": "2.0",
        "method": "test",
        "params": "wrong",
        "id": False
    }

    with pytest.raises(JsonRpcInvalidRequestError):
        JsonRpcRequest.from_dict(jsonrpc_dict)


def test_jsonrpc_request_from_string_fail():
    # invalid json structure
    json1 = '{"jsonrpc": "2.0","method": "test"]'

    with pytest.raises(JsonRpcParseError):
        JsonRpcRequest.from_string(json1)

    # keys without "
    json2 = '{jsonrpc: "2.0",method: "test",params: [1,2,3,4,5],id: 1}'

    with pytest.raises(JsonRpcParseError):
        JsonRpcRequest.from_string(json2)


def test_jsonrpc_request_batch_valid():
    json_items = [
        {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {"a": 1, "b": 2},
            "id": 1
        },
        {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {"a": 3, "b": 4},
            "id": 2
        },
        {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {"a": 5, "b": 6},
            "id": 3
        }
    ]

    parsed = JsonRpcRequestBatch.from_json_list(json_items)
    assert len(parsed.items) == 3
    assert [x.id for x in parsed.iter_items()] == [1, 2, 3]
    assert set([x.method for x in parsed.iter_items()]) == {"test"}
    assert [x.params for x in parsed.iter_items()] == [{"a": 1, "b": 2}, {"a": 3, "b": 4}, {"a": 5, "b": 6}]
