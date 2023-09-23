import pytest

from seastar.exceptions import HttpException
from seastar.middleware import ExceptionMiddleware
from seastar.responses import Response


class TestExceptionMiddleware:

    def test_no_exception_raised(self):
        def app(event, context):
            return None

        mw = ExceptionMiddleware(app=app, exception_handlers={})
        assert mw({}, None) is None

    def test_exception_not_handled(self):
        def app(event, context):
            raise Exception

        mw = ExceptionMiddleware(app=app, exception_handlers={})

        with pytest.raises(Exception):
            mw({}, None)
    
    def test_exception_handled(self):
        def app(event, contet):
            raise Exception

        def handler(event, context, exc):
            return "There was an error"
        
        mw = ExceptionMiddleware(app=app, exception_handlers={Exception: handler})
        assert mw({}, None) == "There was an error"

    def test_http_exception_handler(self):
        def app(event, context):
            raise HttpException(400)

        def handler(request, exc: HttpException):
            return Response(exc.detail, exc.status_code)
        
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        mw = ExceptionMiddleware(app=app, exception_handlers={400: handler})
        assert mw(event, None) == {"body": "Bad Request", "statusCode": 400}
    
    def test_add_exception_handler(self):
        def app(event, context):
            return None

        def handler(event, context, exc):
            return None
        
        mw = ExceptionMiddleware(app=app)
        mw.add_exception_handler(Exception, handler)
        assert len(mw.exception_handlers) == 1
        



class TestCreateServerMiddleware:

    def test_debug_handler(self):
        def app(event, context):
            raise Exception("There was an error.")
        
        mw = ExceptionMiddleware.create_server_error_middleware(app=app, debug=True)
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        assert mw(event, None) == {"body": "There was an error.", "statusCode": 500}
    
    def test_default_handler(self):
        def app(event, context):
            raise Exception("There was an error.")

        mw = ExceptionMiddleware.create_server_error_middleware(app=app)
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        assert mw(event, None) == {"body": "Internal Server Error", "statusCode": 500}
        


    
        

        


