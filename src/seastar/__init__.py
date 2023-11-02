from seastar.middleware.exceptions import ExceptionMiddleware
from seastar.requests import Request


def web_function(*, raw: bool = False):
    def decorator(func):
        def wrapper(event, context):
            request = Request.from_event(event)
            response = func(request)
            return response()
        
        app = ExceptionMiddleware(wrapper)
        return app
    return decorator
