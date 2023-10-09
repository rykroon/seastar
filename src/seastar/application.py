from dataclasses import dataclass, field
from typing import Optional

from seastar.exceptions import HttpException
from seastar.handlers import debug_response, error_response, http_exception
from seastar.middleware import ExceptionMiddleware
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
    routes: list[Route] = field(default_factory=list)
    exception_handlers: dict[
        ExceptionHandlerKey, ExceptionHandler
    ] = field(default_factory=dict)
    stack: Optional[EventHandler] = field(default=None, init=False)

    def __post_init__(self):
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

        if error_handler is None:
            error_handler = debug_response if self.debug else error_response

        if HttpException not in exception_handlers:
            exception_handlers[HttpException] = http_exception

        app = Router(routes=self.routes) # inner most layer.
        app = ExceptionMiddleware(app=app, exception_handlers=exception_handlers)
        ... # user middleware goes here.
        app = ExceptionMiddleware(  # outer most layer.
            app=app, exception_handlers={Exception: error_handler}
        )
        return app

    def __call__(self, event: Event, context: Context) -> HandlerResult:
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

    error_handler = debug_response if debug else error_response

    def decorator(func: RequestHandler) -> EventHandler:
        app = Route(path=path, methods=methods, app=func)
        app = ExceptionMiddleware(
            app=app, exception_handlers={
                Exception: error_handler, HttpException: http_exception
            }
        )

        def wrapper(event: Event, context: Context) -> HandlerResult:
            return app(event, context)

        return wrapper
    return decorator
