from typing import Callable, Optional
from seastar.middleware.exceptions import ExceptionMiddleware
from seastar.routing import Route
from seastar.types import WebHandler, EventHandler


def web_function(path: str = "", /, *, methods: Optional[list[str]] = None) -> Callable[[WebHandler], EventHandler]:
    def decorator(func: WebHandler) -> EventHandler:
        route = Route(path=path, endpoint=func, methods=methods)  
        app = ExceptionMiddleware(route)
        return app
    return decorator
