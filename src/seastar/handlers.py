from http import HTTPStatus
import traceback

from seastar.exceptions import HttpException
from seastar.requests import Request
from seastar.responses import PlainTextResponse, Response

"""
Default handlers
"""


def http_exception(request: Request, exc: HttpException) -> Response:
    # default handler fot http exception.
    return PlainTextResponse(
        body=exc.message, status_code=exc.status_code, headers=exc.headers
    )


def debug_response(request: Request, exc: Exception) -> Response:
    # in the future this should return an html page with the traceback.
    body = "".join(traceback.format_exception(exc))
    return PlainTextResponse(body=body, status_code=500)


def error_response(request: Request, exc: Exception) -> Response:
    status = HTTPStatus(500)
    return PlainTextResponse(status.phrase, status.value)
