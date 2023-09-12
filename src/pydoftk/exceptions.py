from dataclasses import dataclass


@dataclass
class HttpException(Exception):
    message: str
    status_code: int
