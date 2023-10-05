

from seastar.application import SeaStar, seastar

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
        app = SeaStar()
        assert app(event, None) == {
            "body": "Not Found",
            "statusCode": 404,
            "headers": {"content-type": "text/plain"}
        }

    def test_custom_exception_handlers(self):
        def error_handler(event, context, exc):
            return "There was an error."

        def runtime_handler(event, context, exc):
            return "there was a runtime error."
        
        def my_route(request):
            raise RuntimeError()
        
        app = SeaStar(
            routes=[Route(path="", methods=["GET"], app=my_route)],
            exception_handlers={Exception: error_handler, RuntimeError: runtime_handler}
        )
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        assert app(event, None) == "there was a runtime error."



class TestSeaStarDecorator:

    def test_seastart(self):
        @seastar(path="")
        def my_route(request):
            return Response("hello world")
        
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        assert my_route(event, None) == {"body": "hello world"}
