import pytest

from seastar.endpoints import HttpEndpoint
from seastar.exceptions import HttpException
from seastar.routing import Route, Router
from seastar.responses import Response


@pytest.fixture
def endpoint():
    def endpoint(request):
        return Response("OK")

    return endpoint


class TestRoute:
    def test_not_found(self, endpoint):
        route = Route("path", methods=["GET"], endpoint=endpoint)
        event = {"http": {"path": "", "method": "GET", "headers": {}},}

        # The route IS the entry point.
        assert route(event, None) == {"body": "Not Found", "statusCode": 404}
        
        # the route is NOT the entry point.
        event["__seastar"]["entry_point"] = object()
        with pytest.raises(HttpException):
            route(event, None)

    def test_method_not_allowed(self, endpoint):
        route = Route("", methods=["POST"], endpoint=endpoint)
        event = {"http": {"path": "", "method": "GET", "headers": {}},}

        # The route IS the entry point.
        assert route(event, None) == {
            "body": "Method Not Allowed", "statusCode": 405, "headers": {"Allow": "POST"}
        }
        
        # the route is NOT the entry point.
        event["__seastar"]["entry_point"] = object()
        with pytest.raises(HttpException):
            route(event, None)
    
    def test_http_endpoint(self):
        class MyEndpoint(HttpEndpoint):
            ...

        route = Route("", methods=["GET"], endpoint=MyEndpoint)
        assert isinstance(route.handler, HttpEndpoint)

    def test_success(self, endpoint):
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        route = Route("", methods=["GET"], endpoint=endpoint)

        assert route(event, None) == {"body": "OK"}


class TestRouter:
    def test_not_found(self, endpoint):
        event = {
            "http": {"path": "", "method": "GET", "headers": {}},
            "__seastar": {"entry_point": None},
        }
        route = Route("/path", methods=["GET"], endpoint=endpoint)
        router = Router(routes=[route])

        with pytest.raises(HttpException):
            router(event, None)

    def test_method_not_allowed(self, endpoint):
        event = {
            "http": {"path": "", "method": "GET", "headers": {}},
            "__seastar": {"entry_point": None},
        }
        route = Route("", methods=["POST"], endpoint=endpoint)
        router = Router(routes=[route])

        with pytest.raises(HttpException):
            router(event, None)

    def test_success(self, endpoint):
        event = {
            "http": {"path": "", "method": "GET", "headers": {}},
        }
        route = Route("", methods=["GET"], endpoint=endpoint)
        router = Router(routes=[route])
        assert router(event, None) == {"body": "OK"}

    def test_add_route(self, endpoint):
        router = Router()
        router.add_route("", methods=["GET"], endpoint=endpoint)
        assert len(router.routes) == 1
        assert isinstance(router.routes[0], Route)
