from seastar import exception_handler, function, Request, EXCEPTION_HANDLERS, HttpException
from seastar.handlers import http_handler, default_handler
import pytest


@pytest.fixture(autouse=True)
def clear_exceptions():
    EXCEPTION_HANDLERS.clear()


def test_http_handler():
    exc = HttpException(400, "shit!")
    result = http_handler(None, exc)
    assert result == ("shit!", 400, None)


def test_default_handler():
    exc = Exception("shit")
    result = default_handler(None, exc)
    assert result == ("Internal Server Error", 500)



class TestErrorHandler:
    def test_catch_exception(self):
        @exception_handler(RuntimeError)
        def handle_exception(request, exc):
            assert isinstance(request, Request)
            assert isinstance(exc, Exception)
            return "Error!", 500

        @function
        def my_function(request):
            assert isinstance(request, Request)
            raise RuntimeError

        event = {
            "http": {
                "body": "",
                "headers": {},
                "method": "GET",
                "path": "",
                "queryString": "a=1",
            }
        }

        result = my_function(event)
        assert result["body"] == "Error!"
        assert result["statusCode"] == 500

    def test_catch_exception_subclass(self):
        """
        The error handler handles the built-in Exception class.
        But it should still catch errors that are subclasses.
        """

        @exception_handler(Exception)
        def handle_exception(request, exc):
            assert isinstance(request, Request)
            assert isinstance(exc, Exception)
            return "Error!", 500

        @function
        def my_function(request):
            assert isinstance(request, Request)
            raise RuntimeError

        event = {
            "http": {
                "body": "",
                "headers": {},
                "method": "GET",
                "path": "",
                "queryString": "a=1",
            }
        }

        result = my_function(event)
        assert result["body"] == "Error!"
        assert result["statusCode"] == 500

    def test_unhandled_exception(self):
        """
        The error handler handles the built-in Exception class.
        But it should still catch errors that are subclasses.
        """

        @function
        def my_function(request):
            assert isinstance(request, Request)
            raise Exception

        event = {
            "http": {
                "body": "",
                "headers": {},
                "method": "GET",
                "path": "",
                "queryString": "a=1",
            }
        }

        with pytest.raises(Exception):
            my_function(event)
