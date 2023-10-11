from dataclasses import dataclass, field
from typing import Optional

from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.types import (
    Context,
    Event,
    EventExceptionHandler,
    ExceptionHandler,
    ExceptionHandlerKey,
    EventHandler,
    HandlerResult,
    RequestExceptionHandler
)


def request_response(handler: RequestExceptionHandler) -> EventExceptionHandler:
    def wrapper(event: Event, context: Context, exc: Exception) -> HandlerResult:
        request = Request.from_event(event)
        response = handler(request, exc)
        return response.to_result()
    return wrapper


@dataclass
class ExceptionMiddleware:
    handler: EventHandler
    exception_handlers: dict[
        ExceptionHandlerKey, ExceptionHandler
    ] = field(default_factory=dict)

    def __post_init__(self) -> None:
        exception_handlers = {}
        for key, value in self.exception_handlers.items():
            if isinstance(key, int) or issubclass(key, HttpException):
                value = request_response(value)
            exception_handlers[key] = value
        self.exception_handlers = exception_handlers

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        try:
            return self.handler(event, context)

        except Exception as e:
            handler = self.lookup_handler(e)
            if handler is None:
                raise e

            return handler(event, context, e)

    def lookup_handler(self, exc: Exception) -> Optional[ExceptionHandler]:
        if isinstance(exc, HttpException):
            if exc.status_code in self.exception_handlers:
                return self.exception_handlers[exc.status_code]

        for exc_class in type(exc).mro()[:-2]:
            if exc_class in self.exception_handlers:
                return self.exception_handlers[exc_class]

        return None

    def add_exception_handler(
        self, key: ExceptionHandlerKey, handler: ExceptionHandler
    ) -> None:
        self.exception_handlers[key] = handler
