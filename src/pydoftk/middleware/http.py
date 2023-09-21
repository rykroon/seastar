from dataclasses import dataclass
from typing import Any, Callable

from pydoftk.types import Request, Response


@dataclass
class RequestResponseMiddleware:
    app: Callable[[Request], Response]

    def __call__(self, event, _) -> Any:
        request = Request.from_event(event)
        response = self.app(request)
        return response()
