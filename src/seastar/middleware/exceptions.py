from dataclasses import dataclass, field
from typing import Any, Optional

from seastar.exceptions import HttpException
from seastar.middleware.web import WebEventMiddleware
from seastar.types import (
    Context, Event, EventHandler, ExceptionHandler, ExceptionHandlerKey
)


@dataclass
class ExceptionMiddleware:
    app: EventHandler
    exception_handlers: dict[
        ExceptionHandlerKey, ExceptionHandler
    ] = field(default_factory=dict)

    def __post_init__(self):
        exception_handlers = {}
        for key, value in self.exception_handlers.items():
            if isinstance(key, int) or issubclass(key, HttpException):
                value = WebEventMiddleware(value, is_exception_handler=True)
            exception_handlers[key] = value
        self.exception_handlers = exception_handlers

    def __call__(self, event: Event, context: Context) -> Any:
        try:
            return self.app(event, context)

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
    ):
        self.exception_handlers[key] = handler
