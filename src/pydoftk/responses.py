from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Response:
    body: Any
    status_code: Optional[int] = None
    headers: Optional[dict[str, str]] = None

    def __call__(self):
        result = {}
        if self.body is not None:
            result["body"] = self.body

        if self.status_code is not None:
            result["statusCode"] = self.status_code

        if self.headers is not None:
            result["headers"] = self.headers

        return result or None
