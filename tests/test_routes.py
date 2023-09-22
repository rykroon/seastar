import pytest

from seastar.exceptions import HttpException
from seastar.routes import Route, Router, request_response
from seastar.responses import Response


def test_request_response():

    @request_response
    def endpoint(request):
        return Response("OK")

    event = {"http": {"path": "", "method": "GET", "headers": {}}}
    assert endpoint(event, None) == {"body": "OK"}


class TestRoute:

    def test_not_found(self):
        def endpoint(request):
            return Response("OK")
        
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        route = Route("path", methods=["GET"], endpoint=endpoint)

        assert route.matches("path", "GET") == (True, True)

        with pytest.raises(HttpException):
            route(event, None)

    def test_method_not_allowed(self):
        def endpoint(request):
            return Response("OK")
        
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        route = Route("", methods=["POST"], endpoint=endpoint)

        with pytest.raises(HttpException):
            route(event, None)

    def test_success(self):
        def endpoint(request):
            return Response("OK")
        
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        route = Route("", methods=["GET"], endpoint=endpoint)

        assert route(event, None) == {"body": "OK"}


class TestRouter:

    def test_router(self):
        ...
