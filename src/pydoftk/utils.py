from functools import wraps
from typing import Any, Callable

from .handlers import EXCEPTION_HANDLERS
from .requests import Request
from .responses import Response


def function(
    func: Callable[[Request], Any]
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    @wraps(func)
    def wrapper(event: dict[str, Any]) -> dict[str, Any]:
        request = Request.from_event(event)
        try:
            result = func(request)

        except Exception as e:
            for exc_class in type(e).mro()[:-2]:
                if exc_class in EXCEPTION_HANDLERS:
                    result = EXCEPTION_HANDLERS[exc_class](request, e)
                    break
            else:
                raise e

        return Response.from_any(result).to_dict()
    return wrapper
