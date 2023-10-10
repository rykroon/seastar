from collections.abc import Mapping
from http import HTTPStatus
from typing import Optional

from seastar.datastructures import MutableHeaders


class HttpException(Exception):

    def __init__(
        self,
        status_code: int,
        message: Optional[str],
        headers: Optional[Mapping[str, str]]
    ) -> None:
        self.status_code = status_code
        self.message = message or HTTPStatus(self.status_code).phrase
        self.headers = MutableHeaders(headers)
        super().__init__(self.status_code, self.message)
