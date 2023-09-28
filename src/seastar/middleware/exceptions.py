from dataclasses import dataclass, field
from typing import Optional

from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.types import App, ExceptionHandler, ExceptionHandlerKey


@dataclass
class ExceptionMiddleware:
    app: App
    exception_handlers: dict[
        ExceptionHandlerKey, ExceptionHandler
    ] = field(default_factory=dict)

    def __call__(self, event, context):
        try:
            return self.app(event, context)

        except Exception as e:
            handler = self.lookup_handler(e)
            if handler is None:
                raise e

            request = Request.from_event(event)
            response = handler(request, e)
            return response()

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
