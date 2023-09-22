from seastar import Response


class TestProcessResponse:
    def test_any(self):
        assert Response.from_any("Hello World").to_dict() == {"body": "Hello World"}

    def test_response_body(self):
        result = Response("Hello World")
        assert result.to_dict() == {"body": "Hello World"}

    def test_response_status_code(self):
        result = Response("Hello World", status_code=200)
        assert result.to_dict() == {"body": "Hello World", "statusCode": 200}

    def test_response_headers(self):
        result = Response("Hello World", status_code=200, headers={"foo": "bar"})
        assert result.to_dict() == {
            "body": "Hello World",
            "statusCode": 200,
            "headers": {"foo": "bar"},
        }

    def test_one_tuple(self):
        result = ("Hello World",)
        assert Response.from_any(result).to_dict() == {"body": "Hello World"}

    def test_two_tuple(self):
        result = ("Hello World", 200)
        assert Response.from_any(result).to_dict() == {"body": "Hello World", "statusCode": 200}

    def test_three_tuple(self):
        result = ("Hello World", 200, {"foo": "bar"})
        assert Response.from_any(result).to_dict() == {
            "body": "Hello World",
            "statusCode": 200,
            "headers": {"foo": "bar"},
        }
