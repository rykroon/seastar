from dataclasses import dataclass
import sys
import traceback
from typing import Optional

from seastar.types import (
    Context,
    Event,
    HandlerResult,
    EventHandler,
    EventExceptionHandler,
)


@dataclass
class ServerErrorMiddleware:
    app: EventHandler
    handler: Optional[EventExceptionHandler] = None
    debug: bool = False

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        try:
            return self.app(event, context)

        except Exception as e:
            if self.debug:
                return self.debug_response(event, context, e)

            elif self.handler is None:
                return self.error_response(event, context, e)

            else:
                return self.handler(event, context, e)

    def debug_response(
        self, event: Event, context: Context, exc: Exception
    ) -> HandlerResult:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        # future: update parameters to format_exception after 3.9 is deprecated.
        content = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        return {"body": content, "statusCode": 500}

    def error_response(
        self, event: Event, context: Context, exc: Exception
    ) -> HandlerResult:
        return {"body": "Internal Server Error", "statusCode": 500}
