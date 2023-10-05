from seastar.responses import Response


class TestProcessResponse:
    def test_response_body(self):
        result = Response("Hello World")
        assert result() == {"body": "Hello World"}

    def test_response_status_code(self):
        result = Response("Hello World", status_code=200)
        assert result() == {"body": "Hello World", "statusCode": 200}

    def test_response_headers(self):
        result = Response("Hello World", status_code=200, headers={"foo": "bar"})
        assert result() == {
            "body": "Hello World",
            "statusCode": 200,
            "headers": {"foo": "bar"},
        }
