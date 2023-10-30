import pytest

from seastar.applications import SeaStar
from seastar.responses import Response
from seastar.routing import Route


class TestSeaStarClass:
    def test_route_not_found(self):
        event = {
            "http": {
                "body": "",
                "headers": {},
                "method": "GET",
                "path": "",
                "queryString": "a=1&b=2",
            }
        }
        handler = SeaStar()
        assert handler(event, None) == {
            "body": "Not Found",
            "statusCode": 404,
            "headers": {"content-type": "text/plain"},
        }

    def test_custom_exception_handlers(self):
        def error_handler(event, context, exc):
            return "There was an error."

        def runtime_handler(request, exc):
            return Response("there was a runtime error.", status_code=500)

        def my_route(request):
            raise RuntimeError()

        handler = SeaStar(
            routes=[Route(path="", methods=["GET"], endpoint=my_route)],
            exception_handlers={
                Exception: error_handler,
                RuntimeError: runtime_handler,
            },
        )
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        assert handler(event, None) == {"body": "there was a runtime error.", "statusCode": 500}
    
    def test_add_exception_handler(self):
        app = SeaStar()
        def error_handler(event, context, exc):
            ...

        app.add_exception_handler(Exception, error_handler)
        assert len(app.exception_handlers) == 1
    
    def test_add_middleware(self):
        app = SeaStar()
        class MyMiddleware:
            def __init__(self, app):
                self.app = app

            def __call__(self, event, context):
                return self.app(event, context)

        app.add_middleware(MyMiddleware)
        assert len(app.user_middleware) == 1

        app({}, None)
        with pytest.raises(RuntimeError):
            app.add_middleware(MyMiddleware)
    
    def test_add_route(self):
        app = SeaStar()

        def handler(request):
            ...
        
        app.add_route("", methods=["GET"], endpoint=handler)
        assert len(app.router.routes) == 1
    
    def test_exception_handler_decorator(self):
        app = SeaStar()

        @app.exception_handler(Exception)
        def error_handler(event, context, e):
            ...
        
        assert len(app.exception_handlers) == 1
    
    def test_middleware_decorator(self):
        app = SeaStar()

        @app.middleware(x=1)
        class MyMiddleware:
            def __init__(self, app, x):
                self.app = app
                self.x = x

            def __call__(self, event, context):
                return self.app(event, context)
        
        assert len(app.user_middleware) == 1



# class TestSeaStarDecorator:
#     def test_seastar(self):
#         @seastar("")
#         def my_route(request):
#             return Response("hello world")

#         event = {"http": {"path": "", "method": "GET", "headers": {}}}
#         assert my_route(event, None) == {"body": "hello world", "statusCode": 200}
