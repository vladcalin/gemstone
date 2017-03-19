import urllib.request

import pytest

from gemstone.client.remote_service import RemoteService
import gemstone.errors

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


def test_remote_service_raise_for_type():
    service = RemoteService(DUMMY_SERVICE_URL)

    with pytest.raises(gemstone.errors.MethodNotFoundError):
        service.raise_for_type("method_not_found", "", "")

    with pytest.raises(gemstone.errors.InternalErrorError):
        service.raise_for_type("internal_error", "", "")

    with pytest.raises(gemstone.errors.AccessDeniedError):
        service.raise_for_type("access_denied", "", "")

    with pytest.raises(gemstone.errors.InvalidParamsError):
        service.raise_for_type("invalid_params", "", "")

    with pytest.raises(gemstone.errors.UnknownError):
        service.raise_for_type("unknown", "", "")

    with pytest.raises(gemstone.errors.UnknownError):
        service.raise_for_type("sadqkjqakds", "", "")

    with pytest.raises(gemstone.errors.UnknownError):
        service.raise_for_type("random", "", "")
