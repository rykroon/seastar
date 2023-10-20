from dataclasses import dataclass, field
from typing import Optional

from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.responses import Response, PlainTextResponse
from seastar.types import (
    Context,
    Event,
    ExceptionHandler,
    ExceptionHandlerKey,
    EventHandler,
    HandlerResult,
    RequestExceptionHandler
)


@dataclass
class ExceptionMiddleware:
    app: EventHandler
    handlers: dict[
        ExceptionHandlerKey, RequestExceptionHandler
    ] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.handlers.setdefault(HttpException, self.http_exception)

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        try:
            return self.app(event, context)

        except Exception as e:
            handler = self.lookup_handler(e)
            if handler is None:
                raise e

            request = Request.from_event(event)
            response = handler(request, e)
            return response.to_result()

    def lookup_handler(self, exc: Exception) -> Optional[RequestExceptionHandler]:
        if isinstance(exc, HttpException):
            if exc.status_code in self.handlers:
                return self.handlers[exc.status_code]

        for exc_class in type(exc).mro()[:-2]:
            if exc_class in self.handlers:
                return self.handlers[exc_class]

        return None

    def add_exception_handler(
        self, key: ExceptionHandlerKey, handler: ExceptionHandler
    ) -> None:
        self.handlers[key] = handler
    
    def http_exception(self, request: Request, exc: HttpException) -> Response:
        return PlainTextResponse(
            content=exc.detail, status_code=exc.status_code, headers=exc.headers
        )
