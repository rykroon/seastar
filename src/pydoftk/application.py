from dataclasses import dataclass, field
from typing import Callable

from .exceptions import HttpException
from .middleware import ServerErrorMiddleware, ExceptionMiddleware
from .requests import Request
from .responses import Response
from .routes import Route, Router


@dataclass
class Application:
    debug: bool = False
    routes: list[Route] = field(default_factory=list)
    exception_handlers: dict[type[Exception], Callable] = field(default_factory=dict)

    def __post_init__(self):
        exception_handlers = {}
        error_handler = None
        for k, v in self.exception_handler.items():
            if k in (500, Exception):
                error_handler = v
            else:
                exception_handlers[k] = v
    
        server_error_mw = ServerErrorMiddleware(self, error_handler=error_handler, debug=self.debug)

        router = Router(self.routes)
        app = router
        app = ...
        ...
    
    def build_middleware_stack(self):
        ...

    def __call__(self, event):
        try:
            request = Request.from_event(event)

            for route in self.routes:
                path_match, method_match = route.matches(request)
                if path_match and method_match:
                    break
                elif path_match:
                    raise HttpException(405)
            else:
                raise HttpException(404)

            result = route.func(request)

        except Exception as e:
            for exc_class in type(e).mro()[:-2]:
                if exc_class in self.exception_handlers:
                    result = self.exception_handlers[exc_class](request, e)
                    break
            else:
                raise e

        if not isinstance(result, Response):
            result = Response.from_any(result)
        
        return result.to_dict()

    def route(self, path: str, /, methods: list[str]):
        def decorator(func):
            route = Route(path, func=func, methods=methods)
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
