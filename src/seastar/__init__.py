from seastar.middleware.exceptions import ExceptionMiddleware
from seastar.routing import Route


def web_function(*, raw: bool = False):
    def decorator(func):
        route = Route(path="", endpoint=func)  
        app = ExceptionMiddleware(route)
        return app
    return decorator
