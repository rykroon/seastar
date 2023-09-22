from dataclasses import dataclass, field, InitVar
from typing import Callable

from .exceptions import HttpException, ExceptionMiddleware
from .requests import Request
from .responses import Response
from .routes import Route, Router
from .types import App


@dataclass
class SeaStar:
    debug: bool = False
    routes: InitVar[list[Route]] = field(default_factory=list)
    exception_handlers: InitVar[dict[type[Exception], Callable]] = field(
        default_factory=dict
    )
    router: Router = field(init=False)
    stack: App = field(init=False)

    def __post_init__(self, routes, exception_handlers):
        self.router = Router(routes=routes)
        self.stack = self.router

        # add an additional ExceptionMiddleware layer for Internal Server Errors.
        self.stack = ExceptionMiddleware(
            self.stack, exception_handlers=exception_handlers
        )

    def build_stack(self):
        ...

    def __call__(self, event, context):
        return self.stack(event, context)

    def route(self, path: str, /, methods: list[str]):
        def decorator(func):
            route = Route(path, methods=methods, endpoint=func)
            self.routes.append(route)
            return func

        return decorator

    def get(self, path: str, /):
        return self.route(path, methods=["GET"])

    def post(self, path: str, /):
        return self.route(path, methods=["POST"])

    def exception_handler(self, exc: type[Exception], /):
        def decorator(func):
            self.exception_handlers[exc] = func
            return func

        return decorator
