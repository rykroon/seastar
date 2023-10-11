from collections.abc import Mapping
from http import HTTPStatus
from typing import Optional


class HttpException(Exception):

    def __init__(
        self,
        status_code: int,
        detail: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None
    ) -> None:
        if detail is None:
            detail =  HTTPStatus(status_code).phrase

        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(self.status_code, self.detail)
    
    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"
