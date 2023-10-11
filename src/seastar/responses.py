from collections.abc import Mapping
import json
from typing import Any, ClassVar, Optional

from seastar.json import JsonEncoder
from seastar.types import HandlerResult


class Response:
    media_type: ClassVar[Optional[str]] = None

    def __init__(
        self,
        content: Any = None,
        status_code: Optional[int] = None,
        headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None
    ):
        if headers is None:
            headers = {}

        if media_type is not None:
            self.media_type = media_type

        self.body = self.render(content)
        self.status_code = status_code
        self.headers = headers

        if self.media_type:
            self.headers.setdefault("content-type", self.media_type)

    def render(self, content: Any) -> Any:
        return content

    def to_result(self) -> HandlerResult:
        result = {}
        if self.body is not None:
            result["body"] = self.body

        if self.status_code is not None:
            result["statusCode"] = self.status_code

        if self.headers:
            result["headers"] = dict(self.headers)

        return result


class HtmlResponse(Response):
    media_type = "text/html"


class PlainTextResponse(Response):
    media_type = "text/plain"


class JsonResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> str:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            cls=JsonEncoder,
            indent=None,
            separators=(",", ":")
        )
