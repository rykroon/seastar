from collections.abc import Mapping
from dataclasses import dataclass, field, InitVar
import json
from typing import Any, ClassVar, Optional

from seastar.json import JsonEncoder
from seastar.types import HandlerResult


@dataclass
class Response:
    default_media_type: ClassVar[Optional[str]] = None

    content: InitVar[Any] = None
    status_code: Optional[int] = None
    headers: Mapping[str, str] = field(default_factory=dict)
    media_type: InitVar[Optional[str]] = None

    body: Any = field(init=False)

    def __post_init__(self, content, media_type):
        self.body = self.render(content)
        content_type = media_type or self.default_media_type or None
        if content_type is not None:
            self.headers.setdefault("content-type", content_type)

    # def __init__(
    #     self,
    #     content: Any = None,
    #     status_code: Optional[int] = None,
    #     headers: Optional[Mapping[str, str]] = None,
    #     media_type: Optional[str] = None
    # ):
    #     if headers is None:
    #         headers = {}

    #     if media_type is not None:
    #         self.media_type = media_type

    #     self.body = self.render(content)
    #     self.status_code = status_code
    #     self.headers = headers

    #     if self.media_type:
    #         self.headers.setdefault("content-type", self.media_type)

    def render(self, content: Any) -> Any:
        return content

    def to_result(self) -> HandlerResult:
        result = {}
        if self.body is not None:
            result["body"] = self.body

        if self.status_code is not None:
            result["statusCode"] = self.status_code

        if self.headers:
            result["headers"] = self.headers

        return result


class HtmlResponse(Response):
    default_media_type = "text/html"


class PlainTextResponse(Response):
    default_media_type = "text/plain"


class JsonResponse(Response):
    default_media_type = "application/json"

    def render(self, content: Any) -> str:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            cls=JsonEncoder,
            indent=None,
            separators=(",", ":")
        )
