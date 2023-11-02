from seastar.responses import Response, JSONResponse


class TestResponse:
    def test_response_body(self):
        resp = Response("Hello World")
        assert resp() == {"body": "Hello World", "statusCode": 200, "headers": {"content-length": "11"}}

    def test_response_status_code(self):
        resp = Response("Hello World", status_code=201)
        assert resp() == {"body": "Hello World", "statusCode": 201, "headers": {"content-length": "11"}}

    def test_response_headers(self):
        resp = Response("Hello World", status_code=201, headers={"foo": "bar"}, )
        assert resp() == {
            "body": "Hello World",
            "statusCode": 201,
            "headers": {"content-length": "11", "foo": "bar"},
        }


class TestJsonResponse:
    def test_render(self):
        content = {"hello": "world"}
        resp = JSONResponse(content)
        assert resp.body == '{"hello":"world"}'
