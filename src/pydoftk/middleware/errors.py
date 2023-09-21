from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from pydoftk.types import App, Handler, Request, Response


@dataclass
class ServerErrorMiddleware:
    app: App
    handler: Optional[Handler] = None
    debug: bool = False

    def __call__(self, event, context):
        try:
            return self.app(event, context)

        except Exception as e:
            request = Request.from_event(event)
            if self.debug:
                response = self.debug_response(request, e)
            elif self.handler is None:
                response = self.error_response(request, e)
            else:
                response = self.handler(request, e)

            return response()

    def debug_response(self, request: Request, exc: Exception) -> Response:
        message = f"{type(exc)}: {exc}"
        return Response(message, status_code=500)

    def error_response(self, request: Request, exc: Exception) -> Response:
        return Response(HTTPStatus(500).phrase, status_code=500)
