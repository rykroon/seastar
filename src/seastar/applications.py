from dataclasses import dataclass, field, InitVar
from typing import Any, Callable, Optional

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
    RequestHandler,
)


@dataclass
class App:
    debug: bool = True
    routes: InitVar[Optional[list[Route]]] = None
    middleware: InitVar[Optional[list[Middleware]]] = None
    exception_handlers: dict[ExceptionHandlerKey, ExceptionHandler] = field(
        default_factory=dict
    )

    router: Router = field(init=False)
    user_middleware: list[Middleware] = field(init=False)
    middleware_stack: Optional[EventHandler] = field(init=False, default=None)

    def __post_init__(
        self, routes: Optional[list[Route]], middleware: Optional[list[Middleware]]
    ) -> None:
        routes = [] if routes is None else list(routes)
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
        middleware.append(Middleware(ExceptionMiddleware, handlers=exception_handlers))

        app = self.router
        for mw in reversed(middleware):
            app = mw.cls(app=app, **mw.options)
        return app

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        event.setdefault("__seastar", {}).setdefault("entry_point", self)
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()
        return self.middleware_stack(event, context)

    def add_exception_handler(self, key: ExceptionHandlerKey, func: ExceptionHandler):
        self.exception_handlers[key] = func

    def add_middleware(self, middleware_class: type, **options: Any) -> None:
        if self.middleware_stack is not None:
            raise RuntimeError("Cannot add middleware after an application has started")
        self.user_middleware.insert(0, Middleware(middleware_class, **options))

    def add_route(
        self, path: str, methods: list[str], endpoint: RequestHandler
    ) -> None:
        self.router.add_route(path, methods, endpoint)


@dataclass
class SeaStar(App):

    def exception_handler(self, key: ExceptionHandlerKey):
        def decorator(func):
            self.add_exception_handler(key, func)
            return func

        return decorator

    def middleware(self, **options: Any):
        def decorator(middleware_class: type):
            self.add_middleware(middleware_class, **options)
            return middleware_class

        return decorator

    def route(self, path: str, methods: list[str]):
        return self.router.route(path, methods)

    def get(self, path: str, /):
        return self.router.get(path)

    def post(self, path: str, /):
        return self.router.post(path)

    def put(self, path: str, /):
        return self.router.put(path)

    def patch(self, path: str, /):
        return self.router.delete(path)

    def delete(self, path: str, /):
        return self.router.delete(path)


# def seastar(
#     path: str = "", /, *, methods: Optional[list[str]] = None, debug: bool = False
# ) -> Callable[[RequestHandler], EventHandler]:
#     """
#     A simple decorator for a single function app.
#     Could also work with an HttpEndpoint.
#     """

#     if methods is None:
#         methods = ["GET"]

#     def decorator(func: RequestHandler) -> EventHandler:
#         app = Route(path=path, endpoint=func, methods=methods)
#         app = ExceptionMiddleware(app=app)
#         app = ServerErrorMiddleware(app=app, debug=debug)

#         def wrapper(event: Event, context: Context) -> HandlerResult:
#             event.setdefault("__seastar", {}).setdefault("entry_point", app)
#             return app(event, context)

#         return wrapper

#     return decorator
