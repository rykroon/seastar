from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Optional


HTTP_STATUS_CODES = {
    status.value: status.name.replace("_", " ").title() for status in HTTPStatus
}


@dataclass
class HttpException(Exception):
    status_code: int
    message: Optional[Any] = None   
    headers: Optional[dict[str, str]] = None 

    def __post_init__(self):
        if not self.message:
            self.message = HTTP_STATUS_CODES[self.status_code]
        super().__init__(self.status_code, self.message)


class ConfigurationError(Exception):
    pass
