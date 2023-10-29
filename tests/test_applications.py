from seastar.applications import SeaStar, seastar

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


class TestSeaStarDecorator:
    def test_seastar(self):
        @seastar("")
        def my_route(request):
            return Response("hello world")

        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        assert my_route(event, None) == {"body": "hello world", "statusCode": 200}
