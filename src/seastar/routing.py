from dataclasses import dataclass, field, InitVar
import inspect
from typing import Callable, Union

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

    def __post_init__(
        self, endpoint: Union[type[HttpEndpoint], RequestHandler]
    ) -> None:
        if inspect.isfunction(endpoint) or inspect.ismethod(endpoint):
            self.handler = request_response(endpoint)

        elif inspect.isclass(endpoint) and issubclass(endpoint, HttpEndpoint):
            self.handler = endpoint()

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

    @classmethod
    def route(cls, path: str = "", /, *, methods: list[str]):
        def decorator(endpoint):
            return cls(path, methods, endpoint)
        return decorator

    @classmethod
    def get(cls, path: str = "", /):
        return cls.route(path, methods=["GET"])

    @classmethod
    def post(cls, path: str = "", /):
        return cls.route(path, methods=["POST"])

    @classmethod
    def put(cls, path: str = "", /):
        return cls.route(path, methods=["PUT"])

    @classmethod
    def patch(cls, path: str = "", /):
        return cls.route(path, methods=["PATCH"])

    @classmethod
    def delete(cls, path: str = "", /):
        return cls.route(path, methods=["DELETE"])


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

    def add_route(
        self, path: str, methods: list[str], endpoint: RequestHandler
    ) -> None:
        self.routes.append(Route(path, methods=methods, endpoint=endpoint))

    def route(
        self, path: str, /, *, methods: list[str]
    ) -> Callable[[RequestHandler], RequestHandler]:
        def decorator(func: RequestHandler) -> RequestHandler:
            self.add_route(path, methods, func)
            return func

        return decorator

    def get(self, path: str, /) -> Callable[[RequestHandler], RequestHandler]:
        return self.route(path, methods=["GET"])

    def post(self, path: str, /) -> Callable[[RequestHandler], RequestHandler]:
        return self.route(path, methods=["POST"])

    def put(self, path: str, /) -> Callable[[RequestHandler], RequestHandler]:
        return self.route(path, methods=["PUT"])

    def patch(self, path: str, /) -> Callable[[RequestHandler], RequestHandler]:
        return self.route(path, methods=["PATCH"])

    def delete(self, path: str, /) -> Callable[[RequestHandler], RequestHandler]:
        return self.route(path, methods=["DELETE"])
