from dataclasses import dataclass
from typing import Optional

from seastar.requests import Request
from seastar.types import Context, Event, FunctionResult, WebEventHandler


@dataclass
class WebEventMiddleware:

    app: WebEventHandler
    is_exception_handler: bool = False

    def __call__(
        self, event: Event, context: Context, exc: Optional[Exception] = None
    ) -> FunctionResult:
        request = Request.from_event(event)
        if self.is_exception_handler:
            assert exc is not None
            response = self.app(request, exc)
        else:
            response = self.app(request)
        return response.to_result()
