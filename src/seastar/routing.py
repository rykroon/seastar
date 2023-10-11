from typing import Optional, Union

from seastar.endpoints import HttpEndpoint
from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.responses import PlainTextResponse
from seastar.types import Context, Event, EventHandler, HandlerResult, RequestHandler


def request_response(func: RequestHandler) -> EventHandler:
    def wrapper(event: Event, context: Context) -> HandlerResult:
        request = Request.from_event(event)
        response = func(request)
        return response.to_result()

    return wrapper


class Route:
    def __init__(
        self,
        path: str,
        endpoint: Union[RequestHandler, HttpEndpoint],
        methods: Optional[list[str]],
    ):
        self.path = path

        if isinstance(endpoint, HttpEndpoint):
            self.handler = endpoint()
        else:
            self.handler = request_response(endpoint)

        self.methods = methods

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        assert "http" in event, "Expected a web event."
        is_entry_point = (
            event.setdefault("__seastar", {}).setdefault("entry_point", self) is self
        )

        if self.path != event["http"]["path"]:
            if is_entry_point:
                return PlainTextResponse("Not Found", status_code=404)
            else:
                raise HttpException(404)

        if event["http"]["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            if is_entry_point:
                return PlainTextResponse(
                    "Method Not Allowed", status_code=405, headers=headers
                )
            else:
                raise HttpException(405, headers=headers)

        return self.handler(event, context)

    def matches(self, path: str, method: str) -> tuple[bool, bool]:
        return path == self.path, method in self.methods


class Router:
    def __init__(self, routes: Optional[list[Route]] = None):
        self.routes = [] if routes is None else list(routes)

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        assert "http" in event, "Expected a web event."
        is_entry_point = (
            event.setdefault("__seastar", {}).setdefault("entry_point", self) is self
        )

        path = event["http"]["path"]
        method = event["http"]["method"]

        for route in self.routes:
            path_match, method_match = route.matches(path, method)
            if not path_match:
                continue

            if not method_match:
                headers = {"Allow": ", ".join(route.methods)}
                if is_entry_point:
                    return PlainTextResponse(
                        "Method Not Allowed", status_code=405, headers=headers
                    )
                else:
                    raise HttpException(405, headers=headers)

            return route(event, context)

        if is_entry_point:
            return PlainTextResponse("Not Found", status_code=404)
        else:
            raise HttpException(404)

    def add_route(self, path: str, methods: list[str], endpoint) -> None:
        self.routes.append(Route(path, methods=methods, endpoint=endpoint))

    def route(self, path: str, /, *, methods: list[str]):
        def decorator(func):
            self.add_route(path, methods, func)

        return decorator

    def get(self, path: str):
        return self.route(path, methods=["GET"])

    def post(self, path: str):
        return self.route(path, methods=["POST"])
