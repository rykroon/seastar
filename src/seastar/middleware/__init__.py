from typing import Any, Iterator


class Middleware:
    def __init__(self, cls: type, **options: Any):
        self.cls = cls
        self.options = options

    def __iter__(self) -> Iterator[object]:
        """
        mypy issue with annotating iterators.
        https://github.com/python/mypy/issues/15408
        """
        t = (self.cls, self.options)
        i = iter(t)
        return i
