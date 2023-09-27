from dataclasses import dataclass
from typing import Any, Optional

from seastar.datastructures import MutableHeaders


@dataclass
class Response:
    body: Any = None
    status_code: Optional[int] = None
    headers: Optional[MutableHeaders[str, str]] = None

    def __post_init__(self):
        if self.headers is not None and not isinstance(self.headers, MutableHeaders):
            self.headers = MutableHeaders(self.headers)

    def __call__(self):
        result = {}
        if self.body is not None:
            result["body"] = self.body

        if self.status_code is not None:
            result["statusCode"] = self.status_code

        if self.headers:
            result["headers"] = self.headers

        return result or None


class HtmlResponse(Response):
    ...


class PlainTextResponse(Response):
    ...


class JsonResponse(Response):
    ...
