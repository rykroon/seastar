from urllib.parse import parse_qsl, urlencode
from typing_extensions import Self

from multidict import MultiDict, MultiDictProxy, CIMultiDict, CIMultiDictProxy


class ImmutableMultiDict(MultiDictProxy[str, str]):
    def __init__(self, *args, **kwargs):
        super().__init__(MultiDict(*args, **kwargs))


class ImmutableCIMultiDict(CIMultiDictProxy[str, str]):
    def __init__(self, *args, **kwargs):
        super().__init__(CIMultiDict(*args, **kwargs))


class UrlFormEncodedDict(ImmutableMultiDict[str, str]):
    def __str__(self):
        return urlencode(self)

    @classmethod
    def from_string(cls, s: str, /) -> Self:
        return cls(parse_qsl(s))


class QueryParams(UrlFormEncodedDict[str, str]):
    pass


class FormData(UrlFormEncodedDict[str, str]):
    pass


class Headers(ImmutableCIMultiDict[str, str]):
    pass


class MutableHeaders(CIMultiDict[str, str]):
    pass
