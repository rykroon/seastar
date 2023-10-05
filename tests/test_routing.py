import pytest

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
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        route = Route("path", methods=["GET"], app=endpoint)

        assert route.matches("path", "GET") == (True, True)

        with pytest.raises(HttpException):
            route(event, None)

    def test_method_not_allowed(self, endpoint):
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        route = Route("", methods=["POST"], app=endpoint)

        with pytest.raises(HttpException):
            route(event, None)

    def test_success(self, endpoint):
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        route = Route("", methods=["GET"], app=endpoint)

        assert route(event, None) == {"body": "OK"}


class TestRouter:
    def test_not_found(self, endpoint):
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        route = Route("/path", methods=["GET"], app=endpoint)
        router = Router(routes=[route])

        with pytest.raises(HttpException):
            router(event, None)

    def test_method_not_allowed(self, endpoint):
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        route = Route("", methods=["POST"], app=endpoint)
        router = Router(routes=[route])

        with pytest.raises(HttpException):
            router(event, None)

    def test_success(self, endpoint):
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        route = Route("", methods=["GET"], app=endpoint)
        router = Router(routes=[route])
        assert router(event, None) == {"body": "OK"}

    def test_add_route(self, endpoint):
        router = Router()
        route = Route("", methods=["GET"], app=endpoint)
        router.add_route(route)
        assert len(router.routes) == 1
