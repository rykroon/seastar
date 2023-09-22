from base64 import b64decode
import pytest

from seastar import Request
from seastar.exceptions import ConfigurationError


class TestRequest:

    def test_configuration_error(self):
        event = {}

        with pytest.raises(ConfigurationError):
            Request.from_event_context(event)
    
        event = {
            "http": {"headers": {}, "method": "GET", "Path": ""}
        }

        with pytest.raises(ConfigurationError):
            Request.from_event_context(event)

    def test_get(self):
        event = {
            "http": {
                "body": "",
                "headers": {},
                "method": "GET",
                "path": "",
                "queryString": "a=1",
            }
        }

        request = Request.from_event_context(event)
        assert request.body == event["http"]["body"]
        assert request.headers == event["http"]["headers"]
        assert request.method == event["http"]["method"]
        assert request.path == event["http"]["path"]
        assert dict(request.query_params) == {"a": "1"}

    def test_post_with_json(self):
        event = {
            "http": {
                "body": '{"a": 1}',
                "headers": {
                    "content-type": "application/json",
                },
                "isBase64Encoded": False,
                "method": "POST",
                "path": "",
                "queryString": "",
            }
        }

        request = Request.from_event_context(event)
        assert request.body == event["http"]["body"]
        assert request.headers == event["http"]["headers"]
        assert request.method == event["http"]["method"]
        assert request.path == event["http"]["path"]
        assert dict(request.query_params) == {}
        assert request.json() == {"a": 1}

    def test_post_with_form(self):
        event = {
            "http": {
                "body": "a=1",
                "headers": {
                    "content-type": "application/x-www-form-urlencoded",
                },
                "isBase64Encoded": False,
                "method": "POST",
                "path": "",
                "queryString": "",
            }
        }

        request = Request.from_event_context(event)
        assert request.body == event["http"]["body"]
        assert request.headers == event["http"]["headers"]
        assert request.method == event["http"]["method"]
        assert request.path == event["http"]["path"]
        assert dict(request.query_params) == {}
        assert dict(request.form()) == {"a": "1"}

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
        assert request.body == b64decode(event["http"]["body"]).decode()
        assert request.headers == event["http"]["headers"]
        assert request.method == event["http"]["method"]
        assert request.path == event["http"]["path"]
        assert dict(request.query_params) == {}