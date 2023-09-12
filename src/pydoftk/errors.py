from http import HTTPStatus
from typing import Any, Callable

from .exceptions import HttpException
from .requests import Request


HTTP_STATUS_CODES = {
    status.value: status.name.replace("_", " ").title() for status in HTTPStatus
}


def http_handler(request: Request, exc: HttpException):
    return HTTP_STATUS_CODES[exc.status_code], exc.status_code


def default_handler(request: Request, exc: Exception):
    return HTTP_STATUS_CODES[500], 500


EXCEPTION_HANDLERS = {
    HttpException: http_handler,
    Exception: default_handler,
}


def error_handler(
    exc_class: type[Exception], /
) -> Callable[[Callable[[Request, Exception], Any]], Any]:
    def decorator(func: Callable[[Request, Exception], Any]) -> Any:
        EXCEPTION_HANDLERS[exc_class] = func
        return func

    return decorator
