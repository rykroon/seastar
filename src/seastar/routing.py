from dataclasses import dataclass, field, InitVar
import inspect

from starlette.exceptions import HTTPException

from seastar.requests import Request
from seastar.types import Context, Event, EventHandler, HandlerResult, RequestHandler


def request_response(func: RequestHandler) -> EventHandler:
    def wrapper(event: Event, context: Context) -> HandlerResult:
        request = Request.from_event(event)
        response = func(request)
        return response()

    return wrapper


@dataclass
class Route:
    path: str
    methods: list[str]
    endpoint: InitVar[RequestHandler]
    handler: EventHandler = field(init=False)

    def __post_init__(
        self, endpoint: RequestHandler
    ) -> None:
        if inspect.isfunction(endpoint) or inspect.ismethod(endpoint):
            self.handler = request_response(endpoint)

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        assert "http" in event, "Expected a web event."
        is_entry_point = (
            event.setdefault("__seastar", {}).setdefault("entry_point", self) is self
        )

        if self.path != event["http"]["path"]:
            if not is_entry_point:
                raise HTTPException(404)

            return {"body": "Not Found", "statusCode": 404}

        if event["http"]["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            if not is_entry_point:
                raise HTTPException(405, headers=headers)

            return {"body": "Method Not Allowed", "statusCode": 405, "headers": headers}

        return self.handler(event, context)

    def matches(self, path: str, method: str) -> tuple[bool, bool]:
        return path == self.path, method in self.methods


@dataclass
class Router:
    routes: list[Route] = field(default_factory=list)

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
                    raise HTTPException(405, headers=headers)

                return {
                    "body": "Method Not Allowed",
                    "statusCode": 405,
                    "headers": headers,
                }

            return route(event, context)

        if not is_entry_point:
            raise HTTPException(404)

        return {"body": "Not Found", "statusCode": 404}

    def add_route(
        self, path: str, methods: list[str], endpoint: RequestHandler
    ) -> None:
        self.routes.append(Route(path, methods=methods, endpoint=endpoint))

