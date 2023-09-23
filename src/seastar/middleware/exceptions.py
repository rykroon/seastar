from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Optional, Union

from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.responses import Response
from seastar.types import App, ExceptionHandler, HttpExceptionHandler


@dataclass
class ExceptionMiddleware:
    app: App
    exception_handlers: dict[
        Union[type[Exception], int], Union[ExceptionHandler, HttpExceptionHandler]
    ] = field(default_factory=dict)

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

    @classmethod
    def create_server_error_middleware(
        cls,
        app: App,
        handler: Optional[HttpExceptionHandler] = None,
        debug: bool = False
    ):
        """
            Instead of creating a separate ServerError Middleware.
            Just use ExceptionMiddleware.
        """
        if debug:
            handler = cls.debug_response

        elif handler is None:
            handler = cls.error_response

        return cls(app=app, exception_handlers={Exception: handler})

    def lookup_handler(self, exc: Exception) -> Optional[ExceptionHandler]:
        if isinstance(exc, HttpException):
            if exc.status_code in self.exception_handlers:
                return self.exception_handlers[exc.status_code]

        for exc_class in type(exc).mro()[:-2]:
            if exc_class in self.exception_handlers:
                return self.exception_handlers[exc_class]

        return None

    def add_exception_handler(
        self, key: Union[type[Exception], int], handler: ExceptionHandler
    ):
        self.exception_handlers[key] = handler

    @staticmethod
    def debug_response(request: Request, exc: Exception) -> Response:
        # in the future this should return an html page with the traceback.
        return Response(body=str(exc), status_code=500)

    @staticmethod
    def error_response(request: Request, exc: Exception) -> Response:
        status = HTTPStatus(500)
        return Response(status.phrase, status.value)
