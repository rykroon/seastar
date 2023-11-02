import pytest

from starlette.exceptions import HTTPException

from seastar.routing import Route
from seastar.responses import Response


@pytest.fixture
def endpoint():
    def endpoint(request):
        return Response("OK")

    return endpoint


class TestRoute:
    def test_not_found(self, endpoint):
        route = Route("path", methods=["GET"], endpoint=endpoint)
        event = {
            "http": {"path": "", "method": "GET", "headers": {}},
        }

        # The route IS the entry point.
        result = route(event, None)
        assert result["body"] == "Not Found"
        assert result["statusCode"] == 404

        # # the route is NOT the entry point.
        # event["__seastar"]["entry_point"] = object()
        # with pytest.raises(HTTPException):
        #     route(event, None)

    def test_method_not_allowed(self, endpoint):
        route = Route("", methods=["POST"], endpoint=endpoint)
        event = {
            "http": {"path": "", "method": "GET", "headers": {}},
        }

        # The route IS the entry point.
        result = route(event, None)
        assert result["body"] == "Method Not Allowed"
        assert result["statusCode"] == 405
        assert result["headers"]["allow"] == "POST"

        # # the route is NOT the entry point.
        # event["__seastar"]["entry_point"] = object()
        # with pytest.raises(HTTPException):
        #     route(event, None)

    def test_success(self, endpoint):
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        route = Route("", methods=["GET"], endpoint=endpoint)

        assert route(event, None) == {"body": "OK", "statusCode": 200, "headers": {"content-length": "2"}}

