import inspect
import urllib.request
import json

import pytest

from gemstone import as_completed
from gemstone.client.remote_service import RemoteService
from gemstone.client.structs import Result, MethodCall, BatchResult, AsyncMethodCall

DUMMY_SERVICE_URL = "http://example.com/api"


def test_remote_service_initialize():
    service = RemoteService(DUMMY_SERVICE_URL)

    assert service.url == DUMMY_SERVICE_URL


def test_remote_service_make_request_obj():
    service = RemoteService(DUMMY_SERVICE_URL)

    body = {
        "test": "ok"
    }

    req_obj = service.build_http_request_obj(body)

    assert isinstance(req_obj, urllib.request.Request)
    assert req_obj.get_full_url() == DUMMY_SERVICE_URL
    assert req_obj.method == "POST"

    assert req_obj.get_header("Content-Type".capitalize()) == 'application/json'
    assert req_obj.data == b'{"test": "ok"}'


def dummy_urlopen(url, *args, **kwargs):
    class DummyResponse:
        def __init__(self, id=None, *a, **k):
            self.id = id

        def read(self):
            return json.dumps(
                {"jsonrpc": "2.0", "error": None, "result": None, "id": self.id}).encode()

    if not isinstance(url, urllib.request.Request):
        return DummyResponse()

    body = json.loads(url.data.decode())
    return DummyResponse(body.get('id'))


def dummy_urlopen_batch(url, *args, **kwargs):
    class DummyResponse:
        def __init__(self, *ids):
            self.ids = ids

        def read(self):
            return json.dumps([{"jsonrpc": "2.0", "error": None, "result": None, "id": i} for i in
                               self.ids]).encode()

    if not isinstance(url, urllib.request.Request):
        return DummyResponse()

    body = json.loads(url.data.decode())
    ids = [x["id"] for x in body]

    return DummyResponse(*ids)


def test_simple_call(monkeypatch):
    service = RemoteService(DUMMY_SERVICE_URL)

    monkeypatch.setattr(urllib.request, 'urlopen', dummy_urlopen)

    result = service.call_method("test", [])
    assert isinstance(result, Result)
    assert result.id == result.method_call.id


def test_simple_call_notify(monkeypatch):
    service = RemoteService(DUMMY_SERVICE_URL)

    monkeypatch.setattr(urllib.request, 'urlopen', dummy_urlopen)

    result = service.notify("test", [])
    assert result is None


def test_simple_batch_call(monkeypatch):
    service = RemoteService(DUMMY_SERVICE_URL)
    monkeypatch.setattr(urllib.request, 'urlopen', dummy_urlopen_batch)

    calls = [
        MethodCall("test", []),
        MethodCall("test2", []),
        MethodCall("test3", [])
    ]
    result = service.call_batch(*calls)

    assert isinstance(result, BatchResult)
    assert len(result) == 3
    assert result.get_response_for_call(calls[0]).id == calls[0].id
    assert result.get_response_for_call(calls[1]).id == calls[1].id
    assert result.get_response_for_call(calls[2]).id == calls[2].id
    assert result.get_response_for_call(MethodCall("invalid")) is None


def test_async_call(monkeypatch):
    service = RemoteService(DUMMY_SERVICE_URL)
    monkeypatch.setattr(urllib.request, 'urlopen', dummy_urlopen)

    result = service.call_method_async("test", [])
    assert isinstance(result, AsyncMethodCall)

    result = result.result(wait=True)

    assert isinstance(result, Result)
    assert result.id == result.method_call.id


def test_batch_call_errors():
    service = RemoteService(DUMMY_SERVICE_URL)

    with pytest.raises(TypeError):
        service.call_batch(1, 2, 3)


def test_as_completed(monkeypatch):
    service = RemoteService(DUMMY_SERVICE_URL)
    monkeypatch.setattr(urllib.request, 'urlopen', dummy_urlopen)

    items = [service.call_method_async("test", []) for _ in range(10)]

    data = as_completed(*items)

    assert inspect.isgenerator(data)

    results = list(data)
    assert len(results) == 10
