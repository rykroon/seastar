from dataclasses import dataclass, field, InitVar
import inspect
from typing import Optional, Union

from seastar.endpoints import HttpEndpoint
from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.types import Context, Event, EventHandler, HandlerResult, RequestHandler


def request_response(func: RequestHandler) -> EventHandler:
    def wrapper(event: Event, context: Context) -> HandlerResult:
        request = Request.from_event(event)
        response = func(request)
        return response.to_result()

    return wrapper


@dataclass
class Route:
    path: str
    methods: list[str]
    endpoint: InitVar[Union[type[HttpEndpoint], RequestHandler]]
    handler: EventHandler = field(init=False)

    def __post_init__(self, endpoint: Union[type[HttpEndpoint], RequestHandler]):
        if inspect.isclass(endpoint) and issubclass(endpoint, HttpEndpoint):
            self.handler = endpoint()
        else:
            self.handler = request_response(endpoint)

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        assert "http" in event, "Expected a web event."
        is_entry_point = (
            event.setdefault("__seastar", {}).setdefault("entry_point", self) is self
        )

        if self.path != event["http"]["path"]:
            if not is_entry_point:
                raise HttpException(404)

            return {"body": "Not Found", "statusCode": 404}

        if event["http"]["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            if not is_entry_point:
                raise HttpException(405, headers=headers)

            return {"body": "Method Not Allowed", "statusCode": 405, "headers": headers}

        return self.handler(event, context)

    def matches(self, path: str, method: str) -> tuple[bool, bool]:
        return path == self.path, method in self.methods


@dataclass
class Router:
    routes: list[str] = field(default_factory=list)

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
                if not is_entry_point:
                    raise HttpException(405, headers=headers)

                return {
                    "body": "Method Not Allowed",
                    "statusCode": 405,
                    "headers": headers,
                }

            return route(event, context)

        if not is_entry_point:
            raise HttpException(404)

        return {"body": "Not Found", "statusCode": 404}

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
