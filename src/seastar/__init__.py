from typing import Optional
from seastar.middleware.exceptions import ExceptionMiddleware
from seastar.routing import Route


def web_function(path: str = "", /, *, methods: Optional[list[str]] = None):
    def decorator(func):
        route = Route(path=path, endpoint=func, methods=methods)  
        app = ExceptionMiddleware(route)
        return app
    return decorator
