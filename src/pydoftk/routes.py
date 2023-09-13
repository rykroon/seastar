from dataclasses import dataclass
from typing import Callable

from .requests import Request


@dataclass
class Route:
    path: str
    func: Callable
    methods: list[str]

    def matches(self, request: Request) -> tuple[bool, bool]:
        return self.path == request.path, request.method in self.methods
