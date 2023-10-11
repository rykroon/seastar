import pytest

from seastar.exceptions import HttpException
from seastar.middleware import ExceptionMiddleware
from seastar.responses import Response


class TestExceptionMiddleware:
    def test_no_exception_raised(self):
        def handler(event, context):
            return "Hello World"

        mw = ExceptionMiddleware(handler=handler, exception_handlers={})
        assert mw({}, None) == "Hello World"

    def test_exception_not_handled(self):
        def handler(event, context):
            raise RuntimeError("You can't catch me!")

        mw = ExceptionMiddleware(handler=handler, exception_handlers={})

        with pytest.raises(Exception):
            mw({}, None)

    def test_exception_handler(self):
        def handler(event, contet):
            raise Exception

        def exception_handler(event, context, exc):
            return Response("There was an error").to_result()

        mw = ExceptionMiddleware(handler=handler, exception_handlers={Exception: exception_handler})
        assert mw({}, None) == {"body": "There was an error"}

    def test_http_exception_handler(self):
        def handler(event, context):
            raise HttpException(400)

        def exception_handler(request, exc: HttpException):
            return Response(exc.detail, exc.status_code)

        mw = ExceptionMiddleware(handler=handler, exception_handlers={400: exception_handler})
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        assert mw(event, None) == {"body": "Bad Request", "statusCode": 400}

    def test_add_exception_handler(self):
        def handler(event, context):
            return None

        def exception_handler(event, context, exc):
            return None

        mw = ExceptionMiddleware(handler=handler)
        mw.add_exception_handler(Exception, exception_handler)
        assert len(mw.exception_handlers) == 1


