from typing import Any


class Middleware:
    def __init__(self, cls: type, **options: Any):
        self.cls = cls
        self.options = options
