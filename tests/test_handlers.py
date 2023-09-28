

from seastar.handlers import debug_response, error_response
from seastar.requests import Request


def test_debug_response():
    event = {"http": {"headers": {}, "method": "GET", "path": ""}}
    request = Request.from_event(event)

    try:
        raise Exception("There was an error.")
    except Exception as exc:
        response = debug_response(request, exc)
        result = response()
        assert result["statusCode"] == 500
        assert "Traceback" in result["body"]


def test_error_response():    
    event = {"http": {"headers": {}, "method": "GET", "path": ""}}
    request = Request.from_event(event)
    exc = Exception("There was an error.")

    response = error_response(request, exc)
    result = response()
    assert result["statusCode"] == 500
    assert result["body"] == "Internal Server Error"
    assert result["headers"]["content-type"] == "text/plain"
