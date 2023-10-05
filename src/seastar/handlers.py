from http import HTTPStatus
import traceback
from typing import Any

from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.responses import PlainTextResponse, Response
from seastar.types import Context, Event


def http_exception(request: Request, exc: HttpException) -> Response:
    # default handler fot http exception.
    return PlainTextResponse(
        body=exc.message, status_code=exc.status_code, headers=exc.headers
    )


def debug_response(event: Event, context: Context, exc: Exception) -> Any:
    # in the future this should return an html page with the traceback.
    body = "".join(traceback.format_exception(exc))
    if "http" not in event:
        return body

    response = PlainTextResponse(body=body, status_code=500)
    return response()


def error_response(event: Event, context: Context, exc: Exception) -> Any:
    status = HTTPStatus(500)
    if "http" not in event:
        return status.phrase

    response = PlainTextResponse(status.phrase, status.value)
    return response()
