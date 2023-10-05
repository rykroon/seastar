from base64 import b64decode
from seastar.requests import Request


class TestRequest:
    def test_http_get(self):
        event = {
            "http": {
                "body": "",
                "headers": {},
                "method": "GET",
                "path": "",
                "queryString": "a=1&b=2",
            }
        }

        request = Request.from_event(event)
        assert request.body == event["http"]["body"]
        assert request.headers == event["http"]["headers"]
        assert request.method == event["http"]["method"]
        assert request.path == event["http"]["path"]
        assert str(request.query_params) == event["http"]["queryString"]

    def test_http_post_json(self):
        event = {
            "http": {
                "body": '{"a": 1, "b": 2}',
                "headers": {"content-type": "application/json"},
                "isBase64Encoded": False,
                "method": "POST",
                "path": "",
                "queryString": "",
            }
        }

        request = Request.from_event(event)
        assert request.body == event["http"]["body"]
        assert request.headers == event["http"]["headers"]
        assert request.method == event["http"]["method"]
        assert request.path == event["http"]["path"]
        assert str(request.query_params) == ""
        assert request.json() == {"a": 1, "b": 2}

    def test_http_post_form(self):
        event = {
            "http": {
                "body": "a=1&b=2",
                "headers": {
                    "content-type": "application/x-www-form-urlencoded",
                },
                "isBase64Encoded": False,
                "method": "POST",
                "path": "",
                "queryString": "",
            }
        }

        request = Request.from_event(event)
        assert request.body == event["http"]["body"]
        assert request.headers == event["http"]["headers"]
        assert request.method == event["http"]["method"]
        assert request.path == event["http"]["path"]
        assert str(request.query_params) == event["http"]["queryString"]
        assert dict(request.form()) == {"a": "1", "b": "2"}

    def test_post_binary(self):
        event = {
            "http": {
                "body": "aGVsbG8gd29ybGQ=",
                "headers": {
                    "content-type": "application/octet-stream",
                },
                "isBase64Encoded": True,
                "method": "POST",
                "path": "",
                "queryString": "",
            }
        }

        request = Request.from_event(event)
        assert request.body == b64decode(event["http"]["body"].encode()).decode()
        assert request.headers == event["http"]["headers"]
        assert request.method == event["http"]["method"]
        assert request.path == event["http"]["path"]
        assert dict(request.query_params) == {}
