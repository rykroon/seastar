import html
import inspect
import traceback
from typing import Optional

from starlette.middleware.errors import (
    CENTER_LINE,
    FRAME_TEMPLATE,
    JS,
    LINE,
    STYLES,
    TEMPLATE,
)

from seastar.responses import HTMLResponse, PlainTextResponse
from seastar.types import (
    Context,
    Event,
    EventHandler,
    EventExceptionHandler,
    HandlerResult,
)


class ServerErrorMiddleware:
    def __init__(
        self,
        app: EventHandler,
        handler: Optional[EventExceptionHandler] = None,
        debug: bool = False,
    ) -> None:
        self.app = app
        self.debug = debug
        self.handler = handler

    def __call__(self, event: Event, context: Context) -> None:
        _ = event.setdefault("__seastar", {}).setdefault("entry_point", self) is self

        try:
            return self.app(event, context)

        except Exception as exc:
            if self.debug:
                return debug_exception_handler(event, context, exc)

            elif self.handler is not None:
                return self.handler(event, context, exc)

            else:
                return default_exception_handler(event, context, exc)


def default_exception_handler(
    event: Event, context: Context, exc: Exception
) -> HandlerResult:
    response = PlainTextResponse("Internal Server Error", status_code=500)
    return response()


def debug_exception_handler(
    event: Event, context: Context, exc: Exception
) -> HandlerResult:
    accept = event.get("http", {}).get("headers", {}).get("accept", "")

    if "text/html" in accept:
        content = generate_html(exc)
        return HTMLResponse(content, status_code=500)

    content = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    response = PlainTextResponse(content=content, status_code=500)
    return response()


def generate_html(exc: Exception, limit: int = 7) -> str:
    traceback_obj = traceback.TracebackException.from_exception(
        exc, capture_locals=True
    )

    exc_html = ""
    is_collapsed = False
    exc_traceback = exc.__traceback__
    if exc_traceback is not None:
        frames = inspect.getinnerframes(exc_traceback, limit)
        for frame in reversed(frames):
            exc_html += generate_frame_html(frame, is_collapsed)
            is_collapsed = True

    # escape error class and text
    error = (
        f"{html.escape(traceback_obj.exc_type.__name__)}: "
        f"{html.escape(str(traceback_obj))}"
    )

    return TEMPLATE.format(styles=STYLES, js=JS, error=error, exc_html=exc_html)


def generate_frame_html(frame: inspect.FrameInfo, is_collapsed: bool) -> str:
    code_context = "".join(
        format_line(index, line, frame.lineno, frame.index)  # type: ignore[arg-type]
        for index, line in enumerate(frame.code_context or [])
    )

    values = {
        # HTML escape - filename could contain < or >, especially if it's a virtual
        # file e.g. <stdin> in the REPL
        "frame_filename": html.escape(frame.filename),
        "frame_lineno": frame.lineno,
        # HTML escape - if you try very hard it's possible to name a function with <
        # or >
        "frame_name": html.escape(frame.function),
        "code_context": code_context,
        "collapsed": "collapsed" if is_collapsed else "",
        "collapse_button": "+" if is_collapsed else "&#8210;",
    }
    return FRAME_TEMPLATE.format(**values)


def format_line(index: int, line: str, frame_lineno: int, frame_index: int) -> str:
    values = {
        # HTML escape - line could contain < or >
        "line": html.escape(line).replace(" ", "&nbsp"),
        "lineno": (frame_lineno - frame_index) + index,
    }

    if index != frame_index:
        return LINE.format(**values)
    return CENTER_LINE.format(**values)
