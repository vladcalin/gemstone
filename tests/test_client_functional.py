import inspect
import urllib.request
import json
import contextlib
import threading

import pytest

from gemstone.util import first_completed, as_completed
from gemstone.core import MicroService, exposed_method
from gemstone.client.remote_service import RemoteService
from gemstone.client.structs import Result, MethodCall, BatchResult, AsyncMethodCall, Notification


class TestMicroservice(MicroService):
    name = "test_service"

    host = "127.0.0.1"
    port = 9019

    @exposed_method()
    def sum(self, a, b):
        return a + b

    @exposed_method()
    def divide(self, a, b):
        return a / b


@pytest.fixture(scope="module")
def microservice_url():
    service = TestMicroservice()
    threading.Thread(target=service.start).start()
    yield service.accessible_at
    service.get_io_loop().stop()


def test_client_simple_method_call(microservice_url):
    client = RemoteService(microservice_url)

    result = client.call_method("sum", params=[1, 2])
    assert isinstance(result, Result)
    assert result.result == 3

    result = client.call_method("sum", params={"a": 1, "b": 2})
    assert isinstance(result, Result)
    assert result.result == 3


def test_client_simple_method_call_with_errors(microservice_url):
    client = RemoteService(microservice_url)

    # too few positional args
    result = client.call_method("sum", params=[1])
    assert isinstance(result, Result)
    assert result.result is None
    assert result.error["code"] == -32602

    # too many positional args
    result = client.call_method("sum", params=[1, 2, 3])
    assert isinstance(result, Result)
    assert result.result is None
    assert result.error["code"] == -32602

    # too few kw args
    result = client.call_method("sum", params={"a": 1})
    assert isinstance(result, Result)
    assert result.result is None
    assert result.error["code"] == -32602

    # too many kw args
    result = client.call_method("sum", params={"a": 1, "b": 2, "c": 3})
    assert isinstance(result, Result)
    assert result.result is None
    assert result.error["code"] == -32602

    # method not found
    result = client.call_method("invalid", params={"a": 1, "b": 2, "c": 3})
    assert isinstance(result, Result)
    assert result.result is None
    assert result.error["code"] == -32601

    # internal error
    result = client.call_method("sum", params=[None, 3])
    assert isinstance(result, Result)
    assert result.result is None
    assert result.error["code"] == -32603


def test_client_simple_method_call_with_objects(microservice_url):
    client = RemoteService(microservice_url)

    req = MethodCall("sum", [1, 2])
    result = client.call_method(req)
    assert isinstance(result, Result)
    assert result.result == 3

    req = MethodCall("sum", {"a": 1, "b": 2})
    result = client.call_method(req)
    assert isinstance(result, Result)
    assert result.result == 3


def test_client_batch_call(microservice_url):
    client = RemoteService(microservice_url)

    requests = [
        MethodCall("sum", [1, 2]),
        MethodCall("divide", [10, 5]),
        MethodCall("sum", [10, -10]),
        MethodCall("sum", ["hello", " world"]),
        MethodCall("sum", [1, 2, 3]),  # error
        Notification("sum", [1, 2])
    ]
    resp = client.call_batch(*requests)
    assert len(resp) == 5
    assert resp.get_response_for_call(requests[0]).result == 3

    assert resp.get_response_for_call(requests[1]).result == 2.

    assert resp.get_response_for_call(requests[2]).result == 0

    assert resp.get_response_for_call(requests[3]).result == "hello world"

    assert resp.get_response_for_call(requests[5]) is None  # it was a notification


def test_client_async_call(microservice_url):
    client = RemoteService(microservice_url)

    async_call = client.call_method_async("sum", [1, 2])
    assert isinstance(async_call, AsyncMethodCall)
    async_call.result(wait=True)
    assert async_call.finished()
    assert async_call.result().result == 3


def test_client_async_as_completed(microservice_url):
    client = RemoteService(microservice_url)

    for ready_result in as_completed(
            *[client.call_method_async("sum", [i, i + 1]) for i in range(10)]):
        print(ready_result)
        assert ready_result.finished()


def test_client_async_first_completed(microservice_url):
    client = RemoteService(microservice_url)

    res = first_completed(*[client.call_method_async("sum", [i, i + 1]) for i in range(10)])

    assert isinstance(res, Result)
    assert res.error is None
    assert isinstance(res.result, int)
    assert 1 <= res.result <= 19
