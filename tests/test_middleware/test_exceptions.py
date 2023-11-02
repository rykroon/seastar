import pytest

from seastar.middleware.exceptions import ExceptionMiddleware


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

    def test_add_exception_handler(self):
        def handler(event, context):
            return None

        def exception_handler(event, context, exc):
            return None

        mw = ExceptionMiddleware(app=handler)
        mw.add_exception_handler(Exception, exception_handler)
        assert len(mw._exception_handlers) == 3

