import pytest

from seastar.exceptions import HttpException
from seastar.middleware.exceptions import ExceptionMiddleware
from seastar.responses import Response


class TestExceptionMiddleware:
    def test_no_exception_raised(self):
        def app(event, context):
            return "Hello World"

        mw = ExceptionMiddleware(app=app, handlers={})
        assert mw({}, None) == "Hello World"

    def test_exception_not_handled(self):
        def app(event, context):
            raise RuntimeError("You can't catch me!")

        mw = ExceptionMiddleware(app=app, handlers={})

        with pytest.raises(Exception):
            mw({}, None)

    def test_exception_handler(self):
        def app(event, contet):
            raise Exception

        def exception_handler(request, exc):
            return Response("There was an error")

        mw = ExceptionMiddleware(app=app, handlers={Exception: exception_handler})
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        assert mw(event, None) == {"body": "There was an error"}

    def test_http_exception_handler(self):
        def app(event, context):
            raise HttpException(400)

        def exception_handler(request, exc: HttpException):
            return Response(exc.detail, exc.status_code)

        mw = ExceptionMiddleware(app=app, handlers={400: exception_handler})
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        assert mw(event, None) == {"body": "Bad Request", "statusCode": 400}

    def test_add_exception_handler(self):
        def handler(event, context):
            return None

        def exception_handler(event, context, exc):
            return None

        mw = ExceptionMiddleware(app=handler)
        mw.add_exception_handler(Exception, exception_handler)
        assert len(mw.handlers) == 2


