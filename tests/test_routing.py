import pytest

from starlette.exceptions import HTTPException

from seastar.routing import BaseRoute, Route, Match
from seastar.exceptions import NonWebFunction
from seastar.requests import Request
from seastar.responses import PlainTextResponse


def test_baseroute_matches():
    route = BaseRoute()
    with pytest.raises(NotImplementedError):
        route.matches({})


def test_baseroute_handle():
    route = BaseRoute()
    with pytest.raises(NotImplementedError):
        route.handle({}, None)


def test_route_init():
    def handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", handler, methods=["POST"])
    assert route.path == "/"
    assert route.endpoint == handler
    assert route.name == "handler"
    assert route.methods == ["POST"]


def test_route_full_match():
    def handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", handler)
    event = {"http": {"method": "GET", "path": "/"}}
    match, _ = route.matches(event)
    assert match == Match.FULL


def test_route_partial_match():
    def handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", handler)
    event = {"http": {"method": "POST", "path": "/"}}
    match, _ = route.matches(event)
    assert match == Match.PARTIAL


def test_route_no_match():
    def handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", handler)
    event = {"http": {"method": "GET", "path": "/not-found"}}
    match, _ = route.matches(event)
    assert match == Match.NONE


def test_route_match_with_path_params():
    def handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/{name}", handler)
    event = {"http": {"method": "GET", "path": "/james"}}
    match, path_params = route.matches(event)
    assert match == Match.FULL
    assert path_params == {"name": "james"}


def test_route_call():
    def handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", handler)
    event = {"http": {"method": "GET", "path": "/"}}
    result = route(event, None)
    assert result["statusCode"] == 200
    assert result["body"] == "Hello, world!"

def test_route_non_web_function():
    def handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", handler)
    event = {}
    with pytest.raises(NonWebFunction):
        route(event, None)


def test_route_not_found():
    def handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", handler)
    event = {"http": {"method": "GET", "path": "/not-found"}}
    result = route(event, None)
    assert result["statusCode"] == 404
    assert result["body"] == "Not Found"


def test_route_handle_return_method_not_allowed():
    def handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", handler, methods=["POST"])
    event = {"http": {"method": "GET", "path": "/"}}
    result = route(event, None)
    assert result["statusCode"] == 405
    assert result["body"] == "Method Not Allowed"
    assert result["headers"]["allow"] == "POST"


def test_route_handle_raise_method_not_allowed():
    def handler(request: Request):
        return PlainTextResponse("Hello, world!")

    route = Route("/", handler, methods=["POST"])
    event = {"http": {"method": "GET", "path": "/"}}
    try:
        route.handle(event, None)
    except HTTPException as exc:
        assert exc.status_code == 405
        assert exc.headers["Allow"] == "POST"
    else:
        assert False, "Expected HTTPException to be raised"
