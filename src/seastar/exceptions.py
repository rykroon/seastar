from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Optional


@dataclass
class HttpException(Exception):
    status_code: int
    message: Optional[Any] = None
    headers: Optional[dict[str, str]] = None

    def __post_init__(self):
        if not self.message:
            self.message = HTTPStatus(self.status_code).phrase
        super().__init__(self.status_code, self.message)
