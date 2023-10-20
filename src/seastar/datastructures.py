from urllib.parse import parse_qsl, urlencode
from typing_extensions import Self

from multidict import MultiDict, MultiDictProxy, CIMultiDict, CIMultiDictProxy


class ImmutableMultiDict(MultiDictProxy):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(MultiDict(*args, **kwargs))


class UrlFormEncodedMixin:
    def __str__(self) -> str:
        return urlencode(self)

    @classmethod
    def from_string(cls, s: str, /) -> Self:
        return cls(parse_qsl(s))


class QueryParams(UrlFormEncodedMixin, ImmutableMultiDict):
    pass


class FormData(UrlFormEncodedMixin, ImmutableMultiDict):
    pass


class Headers(CIMultiDictProxy[str, str]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(CIMultiDict(*args, **kwargs))


class MutableHeaders(CIMultiDict[str, str]):
    pass
