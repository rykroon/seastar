from collections.abc import Mapping
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any, Optional

from seastar.datastructures import MutableHeaders


@dataclass
class HttpException(Exception):
    status_code: int
    message: Optional[Any] = None
    headers: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.message:
            self.message = HTTPStatus(self.status_code).phrase

        if not isinstance(self.headers, MutableHeaders):
            self.headers = MutableHeaders(self.headers)

        super().__init__(self.status_code, self.message)
