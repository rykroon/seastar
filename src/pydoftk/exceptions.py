from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Optional, Union

from .requests import Request
from .types import App, ExceptionHandler, HttpExceptionHandler


@dataclass
class HttpException(Exception):
    status_code: int
    detail: Optional[Any] = None
    headers: Optional[dict[str, str]] = None

    def __post_init__(self):
        if not self.detail:
            self.detail = HTTPStatus(self.status_code).phrase
        super().__init__(self.status_code, self.detail)


@dataclass
class ExceptionMiddleware:
    app: App
    exception_handlers: dict[
        Union[type[Exception], int], Union[ExceptionHandler, HttpExceptionHandler]
    ]

    def __call__(self, event, context):
        try:
            return self.app(event, context)

        except Exception as e:
            handler = self.lookup_handler(e)
            if handler is None:
                raise e

            if "http" in event:
                request = Request.from_event_context(event, context)
                response = handler(request, e)
                return response()

            return handler(event, context, e)

    def lookup_handler(self, exc: Exception) -> Optional[ExceptionHandler]:
        if isinstance(exc, HttpException):
            if exc.status_code in self.exception_handlers:
                return self.exception_handlers[exc.status_code]

        for exc_class in type(exc).mro()[:-2]:
            if exc_class in self.exception_handlers:
                return self.exception_handlers[exc_class]

        return None


def http_exception_handler(request, exc):
    # default http exception handler.
    ...


def server_error_handler(request, exc):
    ...