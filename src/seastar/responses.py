from collections.abc import Mapping
from dataclasses import dataclass, field
import json
from typing import ClassVar, Optional

from seastar.datastructures import MutableHeaders
from seastar.json import JsonEncoder
from seastar.types import FunctionResult, JSON


@dataclass
class Response:
    content_type: ClassVar[Optional[str]] = None

    body: JSON = None
    status_code: Optional[int] = None
    headers: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.headers, MutableHeaders):
            self.headers = MutableHeaders(self.headers)

        if self.content_type:
            self.headers["content-type"] = self.content_type

    # def render_body(self) -> JSON:
    #     return self.body

    def to_result(self) -> FunctionResult:
        result = {}
        if self.body is not None:
            result["body"] = self.body

        if self.status_code is not None:
            result["statusCode"] = self.status_code

        if self.headers:
            result["headers"] = dict(self.headers)

        return result


class HtmlResponse(Response):
    content_type = "text/html"


class PlainTextResponse(Response):
    content_type = "text/plain"


class JsonResponse(Response):
    content_type = "application/json"

    # def render_body(self):
    #     return json.dumps(
    #         self.body,
    #         ensure_ascii=False,
    #         allow_nan=False,
    #         cls=JsonEncoder,
    #         indent=None,
    #         separators=(",", ":")
    #     )
