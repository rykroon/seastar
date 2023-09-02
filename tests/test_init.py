from base64 import b64decode

from pydoftk import process_response, Request, Response, function


class TestRequest:
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

        request = Request.from_event(event)
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

        request = Request.from_event(event)
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

        request = Request.from_event(event)
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

        request = Request.from_event(event)
        assert request.body == b64decode(event["http"]["body"]).decode()
        assert request.headers == event["http"]["headers"]
        assert request.method == event["http"]["method"]
        assert request.path == event["http"]["path"]
        assert dict(request.query_params) == {}


class TestProcessResponse:
    def test_any(self):
        assert process_response("Hello World") == {"body": "Hello World"}

    def test_response_body(self):
        result = Response("Hello World")
        assert process_response(result) == {"body": "Hello World"}

    def test_response_status_code(self):
        result = Response("Hello World", status_code=200)
        assert process_response(result) == {"body": "Hello World", "statusCode": 200}

    def test_response_headers(self):
        result = Response("Hello World", status_code=200, headers={"foo": "bar"})
        assert process_response(result) == {
            "body": "Hello World",
            "statusCode": 200,
            "headers": {"foo": "bar"},
        }

    def test_one_tuple(self):
        result = ("Hello World",)
        assert process_response(result) == {"body": "Hello World"}

    def test_two_tuple(self):
        result = ("Hello World", 200)
        assert process_response(result) == {"body": "Hello World", "statusCode": 200}

    def test_three_tuple(self):
        result = ("Hello World", 200, {"foo": "bar"})
        assert process_response(result) == {
            "body": "Hello World",
            "statusCode": 200,
            "headers": {"foo": "bar"},
        }


def test_function_decorator():
    @function
    def my_function(request):
        assert isinstance(request, Request)
        return "Hello World"

    event = {
        "http": {
            "body": "",
            "headers": {},
            "method": "GET",
            "path": "",
            "queryString": "a=1",
        }
    }

    result = my_function(event)
    assert isinstance(result, dict)
    assert result["body"] == "Hello World"
