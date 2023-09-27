from base64 import b64decode, b64encode
import json
import pytest

from seastar import Request


@pytest.fixture
def get_event():
    return {
        "http": {
            "body": "",
            "headers": {},
            "method": "GET",
            "path": "",
            "queryString": "a=1&b=2"
        }
    }

@pytest.fixture
def json_event():
    body = json.dumps({"a": 1, "b": 2}).encode()
    return {
        "http": {
            "body": b64encode(body).decode(),
            "headers": {"content-type": "application/json"},
            "isBase64Encoded": True,
            "method": "POST",
            "path": "",
            "queryString": "",
        }
    }


@pytest.fixture
def form_event():
    body = b"a=1&b=2"
    return {
        "http": {
            "body": b64encode(body).decode(),
            "headers": {
                "content-type": "application/x-www-form-urlencoded",
            },
            "isBase64Encoded": True,
            "method": "POST",
            "path": "",
            "queryString": "",
        }
    }


def get_decoded_body(event):
    body = event["http"].get("body", "")
    if event["http"].get("isBase64Encoded", False):
        body = b64decode(event["http"]["body"]).decode()
    return body


class TestRequest:

    def test_get(self, get_event):
        request = Request.from_event_context(get_event)
        assert request.body == get_event["http"]["body"]
        assert request.headers == get_event["http"]["headers"]
        assert request.method == get_event["http"]["method"]
        assert request.path == get_event["http"]["path"]
        assert dict(request.query_params) == {"a": "1", "b": "2"}
    
    def test_body_not_encoded(self, json_event):
        request = Request.from_event_context(json_event)
        assert request.body == json_event["http"]["body"]

    def test_post_with_json(self, json_event):
        request = Request.from_event_context(json_event)
        assert request.body == get_decoded_body(json_event)
        assert request.headers == json_event["http"]["headers"]
        assert request.method == json_event["http"]["method"]
        assert request.path == json_event["http"]["path"]
        assert dict(request.query_params) == {}
        assert request.json() == {"a": 1, "b": 2}

    def test_post_with_form(self, form_event):
        request = Request.from_event_context(form_event)
        assert request.body == get_decoded_body(form_event)
        assert request.headers == form_event["http"]["headers"]
        assert request.method == form_event["http"]["method"]
        assert request.path == form_event["http"]["path"]
        assert dict(request.query_params) == {}
        assert dict(request.form()) == {"a": "1", "b": "2"}

    def test_post_with_binary(self):
        event = {
            "http": {
                "body": "SGVsbG8gV29ybGQ=",
                "headers": {
                    "content-type": "application/octet-stream",
                },
                "isBase64Encoded": True,
                "method": "POST",
                "path": "",
                "queryString": "",
            }
        }

        request = Request.from_event_context(event)
        assert request.body == get_decoded_body(event)
        assert request.headers == event["http"]["headers"]
        assert request.method == event["http"]["method"]
        assert request.path == event["http"]["path"]
        assert dict(request.query_params) == {}