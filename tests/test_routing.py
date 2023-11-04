import pytest

from seastar.routing import Route, Match
from seastar.exceptions import NonWebFunction
from seastar.requests import Request
from seastar.responses import PlainTextResponse


def test_route_init():
    def test_handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", test_handler, methods=["POST"])
    assert route.path == "/"
    assert route.endpoint == test_handler
    assert route.name == "test_handler"
    assert route.methods == ["POST"]


def test_route_full_match():
    def test_handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", test_handler)
    event = {"http": {"method": "GET", "path": "/"}}
    match, _ = route.matches(event)
    assert match == Match.FULL


def test_route_partial_match():
    def test_handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", test_handler)
    event = {"http": {"method": "POST", "path": "/"}}
    match, _ = route.matches(event)
    assert match == Match.PARTIAL


def test_route_no_match():
    def test_handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", test_handler)
    event = {"http": {"method": "GET", "path": "/not-found"}}
    match, _ = route.matches(event)
    assert match == Match.NONE


def test_route_match_with_path_params():
    def test_handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/{name}", test_handler)
    event = {"http": {"method": "GET", "path": "/james"}}
    match, path_params = route.matches(event)
    assert match == Match.FULL
    assert path_params == {"name": "james"}


def test_route_call():
    def test_handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", test_handler)
    event = {"http": {"method": "GET", "path": "/"}}
    result = route(event, None)
    assert result["statusCode"] == 200
    assert result["body"] == "Hello, world!"

def test_route_non_web_function():
    def test_handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", test_handler)
    event = {}
    with pytest.raises(NonWebFunction):
        route(event, None)


def test_route_not_found():
    def test_handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", test_handler)
    event = {"http": {"method": "GET", "path": "/not-found"}}
    result = route(event, None)
    assert result["statusCode"] == 404
    assert result["body"] == "Not Found"


def test_route_handle_method_not_allowed():
    def test_handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", test_handler, methods=["POST"])
    event = {"http": {"method": "GET", "path": "/"}}
    result = route(event, None)
    assert result["statusCode"] == 405
    assert result["body"] == "Method Not Allowed"
    assert result["headers"]["allow"] == "POST"
