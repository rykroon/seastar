from typing import Optional

from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.types import Event, Context, HandlerResult, RequestHandler


class HttpEndpoint:

    def __init__(self) -> None:
        self.allowed_methods = [
            method
            for method in ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
            if getattr(self, method.lower(), None) is not None
        ]

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        assert "http" in event, "Expected a web event."
        handler: Optional[RequestHandler] = getattr(self, event["http"]["method"].lower(), None)
        if handler is None:
            headers = {"Allow": ", ".join(self.allowed_methods)}
            raise HttpException(405, headers=headers)

        request = Request.from_event(event)
        response = handler(request)
        return response.to_result()
