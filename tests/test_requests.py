from base64 import b64decode

import pytest

from starlette.exceptions import HTTPException
from seastar.exceptions import NonWebFunction, NotRawHttp

from seastar.requests import Request


def test_not_a_web_event():
    event = {}
    with pytest.raises(NonWebFunction):
        Request(event)


def test_method():
    event = {"http": {"method": "GET"}}
    request = Request(event)
    assert request.method == "GET"


def test_path():
    event = {"http": {"path": "/path"}}
    request = Request(event)
    assert request.path == "/path"


def test_headers():
    event = {"http": {"headers": {}}}
    request = Request(event)
    assert dict(request.headers) == {}


def test_path_params():
    event = {"http": {"path_params": {"param1": "value1", "param2": "value2"}}}
    request = Request(event)
    assert request.path_params == {"param1": "value1", "param2": "value2"}


def test_query_params():
    event = {"http": {"queryString": "param1=value1&param2=value2"}}
    request = Request(event)
    assert dict(request.query_params) == {"param1": "value1", "param2": "value2"}


def test_query_params_not_raw_http():
    event = {"http": {"headers": {}}}
    request = Request(event)
    with pytest.raises(NotRawHttp):
        request.query_params


def test_cookies():
    event = {"http": {"headers": {"cookie": "cookie1=value1; cookie2=value2"}}}
    request = Request(event)
    assert request.cookies == {"cookie1": "value1", "cookie2": "value2"}


def test_cookies_none():
    event = {"http": {"headers": {}}}
    request = Request(event)
    assert request.cookies is None


def test_body():
    event = {"http": {"body": "body"}}
    request = Request(event)
    assert request.body == "body"


def test_body_base64():
    event = {"http": {"body": "Ym9keQ==", "isBase64Encoded": True}}
    request = Request(event)
    assert request.body == "body"


def test_body_not_raw_http():
    event = {"http": {"headers": {}}}
    request = Request(event)
    with pytest.raises(NotRawHttp):
        request.body


def test_parameters():
    event = {"param1": "value1", "param2": "value2", "http": {}}
    request = Request(event)
    assert request.parameters == {"param1": "value1", "param2": "value2"}


def test_json_body():
    event = {
        "http": {
            "body": '{"key": "value"}',
            "headers": {"Content-Type": "application/json"},
        }
    }
    request = Request(event)
    assert request.json() == {"key": "value"}


def test_json_body_not_json():
    event = {"http": {"body": "body", "headers": {"Content-Type": "text/plain"}}}
    request = Request(event)
    with pytest.raises(HTTPException):
        request.json()


def test_json_invalid_json():
    event = {"http": {"body": "body", "headers": {"Content-Type": "text/plain"}}}
    request = Request(event)
    with pytest.raises(HTTPException):
        request.json()

    event = {
        "http": {
            "body": "invalid_json",
            "headers": {"Content-Type": "application/json"},
        }
    }
    request = Request(event)
    with pytest.raises(HTTPException):
        request.json()


def test_form_body():
    event = {
        "http": {
            "body": "key1=value1&key2=value2",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        }
    }
    request = Request(event)
    assert dict(request.form()) == {"key1": "value1", "key2": "value2"}