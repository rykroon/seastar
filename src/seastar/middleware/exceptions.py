from starlette.exceptions import HTTPException
from starlette.middleware import exceptions

from seastar.responses import Response, PlainTextResponse


class ExceptionMiddleware(exceptions.ExceptionMiddleware):
    
    def __call__(self, event, context):
        try:
            return self.app(event, context)

        except Exception as e:
            handler = self.lookup_handler(e)
            if handler is None:
                raise e

            return handler(event, context, e)

    def lookup_handler(self, exc: Exception):
        if isinstance(exc, HTTPException):
            if exc.status_code in self._status_handlers:
                return self._status_handlers[exc.status_code]

        for exc_class in type(exc).mro():
            if exc_class in self._exception_handlers:
                return self._exception_handlers[exc_class]

        return None

    def http_exception(self, event, context, exc: Exception):
        assert isinstance(exc, HTTPException)
        if exc.status_code in {204, 304}:
            return Response(status_code=exc.status_code, headers=exc.headers)
        return PlainTextResponse(
            exc.detail, status_code=exc.status_code, headers=exc.headers
        )

    def websocket_exception(self):
        raise NotImplementedError
