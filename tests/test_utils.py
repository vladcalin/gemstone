import pytest

from gemstone.util import dynamic_load


def test_dynamic_load():
    import urllib.request
    import hashlib
    from urllib.parse import urlparse

    m = dynamic_load("urllib.request")
    assert m == urllib.request

    m = dynamic_load("hashlib")
    assert m == hashlib

    m = dynamic_load("urllib.parse.urlparse")
    assert m == urlparse


def test_dynamic_load_errors():
    with pytest.raises(ImportError):
        dynamic_load("not.existing")

    with pytest.raises(AttributeError):
        dynamic_load("gemstone.core.invalid_stuff")
