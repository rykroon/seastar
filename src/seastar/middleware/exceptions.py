from collections.abc import Mapping
from typing import Optional, Union

from starlette._exception_handler import _lookup_exception_handler
from starlette.exceptions import HTTPException

from seastar.requests import Request
from seastar.responses import Response, PlainTextResponse
from seastar.types import (
    Context,
    Event,
    HandlerResult,
    WebExceptionHandler,
    EventHandler,
)


class ExceptionMiddleware:

    def __init__(
        self,
        app: EventHandler,
        handlers: Optional[Mapping[Union[int, Exception], WebExceptionHandler]] = None,
    ) -> None:
        self.app = app
        self._status_handlers: Mapping[int, WebExceptionHandler] = {}
        self._exception_handlers: Mapping[Exception, WebExceptionHandler] = {
            HTTPException: self.http_exception
        }

        if handlers is not None:
            for key, value in handlers.items():
                self.add_exception_handler(key, value)
    
    def __call__(self, event: Event, context: Context) -> HandlerResult:
        _ = event.setdefault("__seastar", {}).setdefault("entry_point", self) is self

        try:
            return self.app(event, context)

        except Exception as exc:
            handler = self.lookup_handler(exc)
            if handler is None:
                raise exc

            request = Request(event)
            response = handler(request, exc)
            return response()

    
    __code__ = __call__.__code__

    def add_exception_handler(self, key: Union[int, Exception], handler: WebExceptionHandler) -> None:
        if isinstance(key, int):
            self._status_handlers[key] = handler
        else:
            self._exception_handlers[key] = handler

    def lookup_handler(self, exc: Exception):
        if isinstance(exc, HTTPException):
            if exc.status_code in self._status_handlers:
                return self._status_handlers[exc.status_code]

        return _lookup_exception_handler(self._exception_handlers, exc)

    def exception_handler(self, key: Union[int, Exception]  ) -> WebExceptionHandler:
        def decorator(func: WebExceptionHandler) -> WebExceptionHandler:
            self.add_exception_handler(key, func)
            return func
        return decorator
    
    def http_exception(self, request: Request, exc: Exception) -> Response:
        assert isinstance(exc, HTTPException)
        if exc.status_code in {204, 304}:
            return Response(status_code=exc.status_code, headers=exc.headers)

        return PlainTextResponse(
            exc.detail, status_code=exc.status_code, headers=exc.headers
        )
