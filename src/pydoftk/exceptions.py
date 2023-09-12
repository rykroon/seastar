from dataclasses import dataclass


@dataclass
class HttpException(Exception):
    message: str
    status_code: int

    def __post_init__(self):
        super().__init__(self.message, self.status_code)
