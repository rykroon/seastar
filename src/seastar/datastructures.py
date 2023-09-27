from urllib.parse import parse_qsl, urlencode
from multidict import (
    MultiDict, MultiDictProxy, CIMultiDict, CIMultiDictProxy
)


class ImmutableMultiDict(MultiDictProxy):

    def __init__(self, *args, **kwargs):
        super().__init__(MultiDict(*args, **kwargs))


class ImmutableCIMultiDict(CIMultiDictProxy):

    def __init__(self, *args, **kwargs):
        super().__init__(CIMultiDict(*args, **kwargs))


class UrlFormEncodedMixin:

    def __str__(self):
        return urlencode(self)

    @classmethod
    def from_string(cls, s: str, /):
        return cls(parse_qsl(s))


class UrlFormEncodedDict(UrlFormEncodedMixin, ImmutableMultiDict):
    pass
