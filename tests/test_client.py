import urllib.request

import pytest

from gemstone.client.remote_service import RemoteService

SERVICE_URL = "http://example.com/api"


def test_remote_service_initialize():
    service = RemoteService(SERVICE_URL)

    assert service.url == SERVICE_URL


def test_remote_service_make_request_obj():
    service = RemoteService(SERVICE_URL)

    body = {
        "test": "ok"
    }

    req_obj = service.build_request_obj(body)

    assert isinstance(req_obj, urllib.request.Request)
    assert req_obj.get_full_url() == SERVICE_URL
    assert req_obj.method == "POST"

    assert req_obj.get_header("Content-Type".capitalize()) == 'application/json'
    assert req_obj.data == b'{"test": "ok"}'
