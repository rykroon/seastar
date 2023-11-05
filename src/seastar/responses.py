from collections.abc import Mapping
import json
from typing import Any, Optional

from starlette import responses

from seastar.json import JsonEncoder
from seastar.types import HandlerResult


class Response(responses.Response):

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None,
    ) -> None:
        """
            Removed background paramter.
        """
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=None
        )

    def __call__(self) -> HandlerResult:
        result = {"statusCode": self.status_code}
        if self.body is not None:
            result["body"] = self.body

        if self.headers:
            result["headers"] = dict(self.headers)
        
        return result

    def render(self, content: Any) -> Any:
        return content


class HTMLResponse(Response):
    media_type = "text/html"


class PlainTextResponse(Response):
    media_type = "text/plain"


class JSONResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> str:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            cls=JsonEncoder,
            indent=None,
            separators=(",", ":"),
        )
