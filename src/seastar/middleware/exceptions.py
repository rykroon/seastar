from typing import Optional

from starlette.exceptions import HTTPException
from starlette.middleware import exceptions

from seastar.requests import Request
from seastar.responses import Response, PlainTextResponse
from seastar.types import Context, Event, RequestExceptionHandler


class ExceptionMiddleware(exceptions.ExceptionMiddleware):
    
    def __call__(self, event: Event, context: Context):
        try:
            return self.app(event, context)

        except Exception as e:
            handler = self.lookup_handler(e)
            if handler is None:
                raise e

            request = Request(event)
            response = handler(request, e)
            return response()

    def lookup_handler(self, exc: Exception) -> Optional[RequestExceptionHandler]:
        if isinstance(exc, HTTPException):
            if exc.status_code in self._status_handlers:
                return self._status_handlers[exc.status_code]

        for exc_class in type(exc).mro():
            if exc_class in self._exception_handlers:
                return self._exception_handlers[exc_class]

        return None

    def http_exception(self, request: Request, exc: Exception) -> Response:
        assert isinstance(exc, HTTPException)
        if exc.status_code in {204, 304}:
            return Response(status_code=exc.status_code, headers=exc.headers)
        return PlainTextResponse(
            exc.detail, status_code=exc.status_code, headers=exc.headers
        )

    def websocket_exception(self):
        raise NotImplementedError
