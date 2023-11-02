import pytest

from starlette.exceptions import HTTPException

from seastar.endpoints import HttpEndpoint
from seastar.responses import Response


class TestEndpoint:
    def test_method_not_allowed(self):
        class MyEndpoint(HttpEndpoint):
            def get(self, request):
                return Response("Hello World")

        endpoint = MyEndpoint()
        event = {"http": {"path": "", "method": "POST", "headers": {}}}
        result = endpoint(event, None)
        assert result["body"] == "Method Not Allowed"
        assert result["statusCode"] == 405

    def test_method_not_allowed_raise(self):
        class MyEndpoint(HttpEndpoint):
            def get(self, request):
                return Response("Hello World")

        endpoint = MyEndpoint()
        event = {
            "http": {"path": "", "method": "POST", "headers": {}},
            "__seastar": {"entry_point": None},
        }
        with pytest.raises(HTTPException):
            endpoint(event, None)

    def test_success(self):
        class MyEndpoint(HttpEndpoint):
            def get(self, request):
                return Response("Hello World")

        endpoint = MyEndpoint()
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        result = endpoint(event, None)
        assert result["body"] == "Hello World"
