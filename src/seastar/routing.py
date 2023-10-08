from dataclasses import dataclass, field
import inspect

from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.types import Context, Event, Function, FunctionResult, WebFunction


def request_response(func: WebFunction) -> Function:
    def wrapper(event: Event, context: Context) -> FunctionResult:
        request = Request.from_event(event)
        response = func(request)
        return response.to_result()
    return wrapper


@dataclass(order=True)
class Route:
    path: str
    methods: list[str]
    func: Function

    def __post_init__(self) -> None:
        if inspect.isfunction(self.func) or inspect.ismethod(self.func):
            self.func = request_response(self.func)

    def __call__(self, event: Event, context: Context) -> FunctionResult:
        assert "http" in event, "Expected a web event."
        if self.path != event["http"]["path"]:
            raise HttpException(404)

        if event["http"]["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            raise HttpException(405, headers=headers)

        return self.func(event, context)

    def matches(self, path: str, method: str) -> tuple[bool, bool]:
        return path == self.path, method in self.methods


@dataclass
class Router:
    routes: list[Route] = field(default_factory=list)

    def __call__(self, event: Event, context: Context) -> FunctionResult:
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

    def add_route(self, route: Route) -> None:
        self.routes.append(route)

    # def add_route(self, path: str, methods: list[str], app: EventHandler) -> None:
    #     self.routes.append(Route(path, methods, app))
    
    # def route(self, path: str, /, *, methods: list[str]):
    #     def decorator(func):
    #         self.add_route(path, methods, func)
    #     return decorator

    # def get(self, path: str):
    #     return self.route(path, methods=["GET"])
    
    # def post(self, path: str):
    #     return self.route(path, methods=["POST"])

