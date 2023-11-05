import pytest

from starlette.exceptions import HTTPException
from seastar.middleware.exceptions import ExceptionMiddleware
from seastar.responses import PlainTextResponse
from seastar.routing import request_response


def test_status_handlers():
    @request_response
    def app(request):
        raise HTTPException(404)

    def not_found_handler(request, exc):
        return PlainTextResponse("Not Found", status_code=404)

    middleware = ExceptionMiddleware(
        app, handlers={404: not_found_handler}
    )

    event = {"http": {"method": "GET"}}
    response = middleware(event, None)
    assert response["statusCode"] == 404
    assert response["body"] == "Not Found"


def test_http_exception_no_content():
    @request_response
    def app(request):
        raise HTTPException(204)
    
    middleware = ExceptionMiddleware(app)

    event = {"http": {"method": "GET"}}
    response = middleware(event, None)
    assert response["statusCode"] == 204
    assert "body" not in response


def test_http_exception():
    @request_response
    def app(request):
        raise HTTPException(404, "Not Found")

    middleware = ExceptionMiddleware(app)

    event = {"http": {"method": "GET"}}
    response = middleware(event, None)
    assert response["statusCode"] == 404
    assert response["body"] == "Not Found"


def test_exception_not_handled():
    @request_response
    def app(request):
        raise ValueError("Not Found")

    middleware = ExceptionMiddleware(app)

    event = {"http": {"method": "GET"}}

    with pytest.raises(ValueError):
        middleware(event, None)
