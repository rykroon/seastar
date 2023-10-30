from dataclasses import dataclass, field, InitVar
from typing import Optional

from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.responses import Response, PlainTextResponse
from seastar.types import (
    Context,
    Event,
    EventExceptionHandler,
    ExceptionHandler,
    ExceptionHandlerKey,
    EventHandler,
    HandlerResult,
    RequestExceptionHandler,
)


@dataclass
class ExceptionMiddleware:
    app: EventHandler
    handlers: InitVar[Optional[dict[ExceptionHandlerKey, ExceptionHandler]]] = None

    status_handlers: dict[int, RequestExceptionHandler] = field(init=False, default_factory=dict)
    exception_handlers: dict[type[Exception], ExceptionHandler] = field(init=False, default_factory=dict)

    def __post_init__(self, handlers: Optional[dict[ExceptionHandlerKey, ExceptionHandler]]) -> None:
        if handlers is not None:
            for k, v in handlers.items():
                self.add_exception_handler(k, v)

        self.exception_handlers.setdefault(HttpException, self.http_exception)

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
            if exc.status_code in self.status_handlers:
                return self.status_handlers[exc.status_code]

        for exc_class in type(exc).mro()[:-2]:
            if exc_class in self.exception_handlers:
                return self.exception_handlers[exc_class]

        return None

    def add_exception_handler(
        self, key: ExceptionHandlerKey, handler: RequestExceptionHandler
    ) -> None:
        """
        Thinking about adding logic where if the key is an int OR if the key is a
            subclass of HttpException, then automatically wrap with request_response decorator.
        """
        if isinstance(key, int):
            self.status_handlers[key] = handler
        else:
            assert issubclass(key, Exception)
            self.exception_handlers[key] = handler

    def exception_handler(self, key: ExceptionHandlerKey):
        def decorator(handler: ExceptionHandler):
            self.add_exception_handler(key, handler)
        return decorator

    def http_exception(self, request: Request, exc: Exception) -> Response:
        assert isinstance(exc, HttpException)
        return PlainTextResponse(
            content=exc.detail, status_code=exc.status_code, headers=exc.headers
        )
