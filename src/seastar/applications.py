from dataclasses import dataclass, field, InitVar
from typing import Optional

from seastar.middleware import Middleware
from seastar.middleware.errors import ServerErrorMiddleware
from seastar.middleware.exceptions import ExceptionMiddleware
from seastar.routing import Route, Router
from seastar.types import (
    Context,
    Event,
    ExceptionHandlerKey,
    ExceptionHandler,
    EventHandler,
    HandlerResult,
    RequestHandler
)


@dataclass
class SeaStar:
    debug: bool = True
    routes: InitVar[Optional[list[Route]]] = None
    middleware: InitVar[Optional[list[Middleware]]] = None
    exception_handlers: dict[
        ExceptionHandlerKey, ExceptionHandler
    ] = field(default_factory=dict)
    router: Router = field(init=False)
    user_middleware: list[Middleware] = field(init=False)
    middleware_stack: Optional[EventHandler] = field(init=False, default=None)

    def __post_init__(self, routes, middleware) -> None:
        self.router = Router(routes=routes)
        self.user_middleware = [] if middleware is None else list(middleware)

    def build_middleware_stack(self) -> EventHandler:
        error_handler = None
        exception_handlers = {}
        for key, value in self.exception_handlers.items():
            if key in (500, Exception):
                error_handler = value
            else:
                exception_handlers[key] = value

        middleware = []
        middleware.append(
            Middleware(ServerErrorMiddleware, handler=error_handler, debug=self.debug)
        )
        middleware.extend(self.user_middleware)
        middleware.append(
            Middleware(ExceptionMiddleware, handlers=exception_handlers)
        )

        app = self.router
        for cls, options in reversed(middleware):
            app = cls(app=app, **options)
        return app

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        event.setdefault("__seastar", {}).setdefault("entry_point", self)
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()
        return self.middleware_stack(event, context)


def seastar(
    path: str = "", /, *, methods: Optional[list[str]] = None, debug: bool = False
):
    """
        A simple decorator for a single function app.
        Could also work with an HttpEndpoint.
    """

    if methods is None:
        methods = ["GET"]

    def decorator(func: RequestHandler) -> EventHandler:
        app = Route(path=path, endpoint=func, methods=methods)
        app = ExceptionMiddleware(app=app)
        app = ServerErrorMiddleware(app=app, debug=debug)

        def wrapper(event: Event, context: Context) -> HandlerResult:
            event.setdefault("__seastar", {}).setdefault("entry_point", app)
            return app(event, context)

        return wrapper
    return decorator
