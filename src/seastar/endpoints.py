from dataclasses import dataclass, field
from typing import Any

from .exceptions import HttpException
from .requests import Request
from .types import Event, Context


@dataclass
class HttpEndpoint:
    allowed_methods: list[str] = field(init=False)

    def __post_init__(self):
        self.allowed_methods = [
            method
            for method in ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
            if getattr(self, method.lower(), None) is not None
        ]

    def __call__(self, event: Event, context: Context) -> Any:
        assert "http" in event, "Expected a web event."
        handler = getattr(self, event["http"]["method"].lower(), None)
        if handler is None:
            headers = {"Allow": ", ".join(self.allowed_methods)}
            raise HttpException(405, headers=headers)

        request = Request.from_event(event)
        response = handler(request)
        return response()
