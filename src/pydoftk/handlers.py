from typing import Any, Callable

from .exceptions import HttpException
from .requests import Request


def http_handler(request: Request, exc: HttpException):
    return exc.message, exc.status_code, exc.headers


def default_handler(request: Request, exc: Exception):
    return "Internal Server Error", 500


EXCEPTION_HANDLERS = {HttpException: http_handler, Exception: default_handler}


def exception_handler(
    exc_class: type[Exception], /
) -> Callable[[Callable[[Request, Exception], Any]], Any]:
    def decorator(func: Callable[[Request, Exception], Any]) -> Any:
        EXCEPTION_HANDLERS[exc_class] = func
        return func

    return decorator
