from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.types import (
    Context, Event, EventHandler, HandlerResult, RequestHandler
)


def request_response(func: RequestHandler) -> EventHandler:
    def wrapper(event: Event, context: Context) -> HandlerResult:
        request = Request.from_event(event)
        response = func(request)
        return response.to_result()
    return wrapper


class Route:

    def __init__(self, path: str, methods: list[str], handler: RequestHandler):
        self.path: str = path
        self.methods: list[str] = methods
        self.handler: EventHandler = request_response(handler)

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        assert "http" in event, "Expected a web event."
        if self.path != event["http"]["path"]:
            raise HttpException(404)

        if event["http"]["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            raise HttpException(405, headers=headers)

        return self.handler(event, context)

    def matches(self, path: str, method: str) -> tuple[bool, bool]:
        return path == self.path, method in self.methods


class Router:

    def __init__(self, routes: list[Route]):
        self.routes: list[Route] = routes

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        assert "http" in event, "Expected a web event."
        path = event["http"]["path"]
        method = event["http"]["method"]

        for route in self.routes:
            path_match, method_match = route.matches(path, method)
            if not path_match:
                continue

            if not method_match:
                headers = {"Allow": ", ".join(route.methods)}
                raise HttpException(405, headers=headers)

            return route(event, context)

        raise HttpException(404)

    def add_route(self, path: str, methods: list[str], handler: RequestHandler) -> None:
        self.routes.append(Route(path, methods, handler))

    def route(self, path: str, /, *, methods: list[str]):
        def decorator(func):
            self.add_route(path, methods, func)
        return decorator

    def get(self, path: str):
        return self.route(path, methods=["GET"])
    
    def post(self, path: str):
        return self.route(path, methods=["POST"])

