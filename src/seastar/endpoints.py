from dataclasses import dataclass, field
from typing import Optional

from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.responses import PlainTextResponse
from seastar.types import Event, Context, HandlerResult, RequestHandler


@dataclass(eq=False)
class HttpEndpoint:
    allowed_methods: list[str] = field(init=False)

    def __post_init__(self) -> None:
        self.allowed_methods = [
            method
            for method in ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
            if getattr(self, method.lower(), None) is not None
        ]

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        assert "http" in event, "Expected a web event."
        is_entry_point = (
            event.setdefault("__seastar", {}).setdefault("entry_point", self) is self
        )
        handler: Optional[RequestHandler] = getattr(self, event["http"]["method"].lower(), None)
        if handler is None:
            headers = {"Allow": ", ".join(self.allowed_methods)}
            if is_entry_point:
                return PlainTextResponse(
                    "Method Not Allowed", status_code=405, headers=headers
                ).to_result()
            else:
                raise HttpException(405, headers=headers)

        request = Request.from_event(event)
        response = handler(request)
        return response.to_result()
