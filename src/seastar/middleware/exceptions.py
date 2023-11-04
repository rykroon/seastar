from starlette._exception_handler import _lookup_exception_handler
from starlette.exceptions import HTTPException
from starlette.middleware import exceptions

from seastar.requests import Request
from seastar.responses import Response, PlainTextResponse
from seastar.types import Context, Event


class ExceptionMiddleware(exceptions.ExceptionMiddleware):
    
    def __call__(self, event: Event, context: Context):
        _ = event.setdefault("__seastar", {}).setdefault("entry_point", self) is self

        try:
            return self.app(event, context)

        except Exception as exc:
            handler = None

            if isinstance(exc, HTTPException):
                handler = self._status_handlers.get(exc.status_code)
            
            if handler is None:
                handler = _lookup_exception_handler(self._exception_handlers, exc)

            if handler is None:
                raise exc

            request = Request(event)
            response = handler(request, exc)
            return response()

    def http_exception(self, request: Request, exc: Exception) -> Response:
        assert isinstance(exc, HTTPException)
        if exc.status_code in {204, 304}:
            return Response(status_code=exc.status_code, headers=exc.headers)

        return PlainTextResponse(
            exc.detail, status_code=exc.status_code, headers=exc.headers
        )

    def websocket_exception(self):
        raise NotImplementedError
