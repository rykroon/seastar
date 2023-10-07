import pytest

from seastar.exceptions import HttpException
from seastar.middleware import ExceptionMiddleware
from seastar.responses import Response


class TestExceptionMiddleware:
    def test_no_exception_raised(self):
        def app(event, context):
            return "Hello World"

        mw = ExceptionMiddleware(app=app, exception_handlers={})
        assert mw({}, None) == "Hello World"

    def test_exception_not_handled(self):
        def app(event, context):
            raise RuntimeError("You can't catch me!")

        mw = ExceptionMiddleware(app=app, exception_handlers={})

        with pytest.raises(Exception):
            mw({}, None)

    def test_exception_handler(self):
        def app(event, contet):
            raise Exception

        def handler(event, context, exc):
            return Response("There was an error").to_result()

        mw = ExceptionMiddleware(app=app, exception_handlers={Exception: handler})
        assert mw({}, None) == {"body": "There was an error"}

    def test_http_exception_handler(self):
        def app(event, context):
            raise HttpException(400)

        def handler(request, exc: HttpException):
            return Response(exc.message, exc.status_code)

        mw = ExceptionMiddleware(app=app, exception_handlers={400: handler})
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        assert mw(event, None) == {"body": "Bad Request", "statusCode": 400}

    def test_add_exception_handler(self):
        def app(event, context):
            return None

        def handler(event, context, exc):
            return None

        mw = ExceptionMiddleware(app=app)
        mw.add_exception_handler(Exception, handler)
        assert len(mw.exception_handlers) == 1


