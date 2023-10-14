from dataclasses import dataclass, field, InitVar
from typing import Optional

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
    exception_handlers: dict[
        ExceptionHandlerKey, ExceptionHandler
    ] = field(default_factory=dict)
    router: Router = field(init=False)
    stack: Optional[EventHandler] = field(default=None, init=False)

    def __post_init__(self, routes):
        routes = [] if routes is None else list(routes)
        self.router = Router(routes=routes)
        # maybe remove this for performance.
        self.stack = self.build_stack()

    def build_stack(self) -> EventHandler:
        error_handler = None
        exception_handlers = {}
        for key, value in self.exception_handlers.items():
            if key in (500, Exception):
                error_handler = value
            else:
                exception_handlers[key] = value

        app = self.router
        app = ExceptionMiddleware(app=app, handlers=exception_handlers)
        ... # user middleware goes here.
        app = ServerErrorMiddleware(  # outer most layer.
            app=app, handler=error_handler, debug=self.debug
        )
        return app

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        event.setdefault("__seastar", {}).setdefault("entry_point", self)
        if self.stack is None:
            self.stack = self.build_stack()
        return self.stack(event, context)


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
