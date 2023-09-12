from pydoftk import make_response, Response


class TestProcessResponse:
    def test_any(self):
        assert make_response("Hello World") == {"body": "Hello World"}

    def test_response_body(self):
        result = Response("Hello World")
        assert make_response(result) == {"body": "Hello World"}

    def test_response_status_code(self):
        result = Response("Hello World", status_code=200)
        assert make_response(result) == {"body": "Hello World", "statusCode": 200}

    def test_response_headers(self):
        result = Response("Hello World", status_code=200, headers={"foo": "bar"})
        assert make_response(result) == {
            "body": "Hello World",
            "statusCode": 200,
            "headers": {"foo": "bar"},
        }

    def test_one_tuple(self):
        result = ("Hello World",)
        assert make_response(result) == {"body": "Hello World"}

    def test_two_tuple(self):
        result = ("Hello World", 200)
        assert make_response(result) == {"body": "Hello World", "statusCode": 200}

    def test_three_tuple(self):
        result = ("Hello World", 200, {"foo": "bar"})
        assert make_response(result) == {
            "body": "Hello World",
            "statusCode": 200,
            "headers": {"foo": "bar"},
        }
