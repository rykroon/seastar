from dataclasses import dataclass, field

from .exceptions import HttpException
from .requests import Request


@dataclass
class Endpoint:
    allowed_methods: list[str] = field(init=False)

    def __post_init__(self):
        self.allowed_methods = [
            method
            for method in ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
            if getattr(self, method.lower(), None) is not None
        ]

    def __call__(self, event, context):
        request = Request.from_event_context(event, context)
        handler = getattr(self, request.method.lower(), None)
        if handler is None:
            raise HttpException(405)

        response = handler(request)
        return response()
