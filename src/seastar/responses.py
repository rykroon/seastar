from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, ClassVar, Optional

from seastar.datastructures import MutableHeaders


@dataclass
class Response:
    content_type: ClassVar[Optional[str]] = None

    body: Any = None
    status_code: Optional[int] = None
    headers: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.headers, MutableHeaders):
            self.headers = MutableHeaders(self.headers)

        if self.content_type:
            self.headers["content-type"] = self.content_type

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
    content_type = "text/html"


class PlainTextResponse(Response):
    content_type = "text/plain"


class JsonResponse(Response):
    content_type = "application/json"
