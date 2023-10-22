from urllib.parse import parse_qsl, urlencode
from typing import Any, Union

from typing_extensions import Self

from multidict import MultiDict, MultiDictProxy, CIMultiDict, CIMultiDictProxy


class ImmutableMultiDict(MultiDictProxy[str]):
    def __init__(
        self, arg: Union[dict[str, Any], list[tuple[str, Any]], None], **kwargs: Any
    ) -> None:
        arg = {} if arg is None else arg
        super().__init__(MultiDict(arg, **kwargs))


class UrlFormEncodedMixin:
    def __str__(self) -> str:
        return str(urlencode(self))

    @classmethod
    def from_string(cls, s: str, /) -> Self:
        return cls(parse_qsl(s))


class QueryParams(UrlFormEncodedMixin, ImmutableMultiDict):
    pass


class FormData(UrlFormEncodedMixin, ImmutableMultiDict):
    pass


class Headers(CIMultiDictProxy[str]):
    def __init__(
        self, arg: Union[dict[str, Any], list[tuple[str, Any]], None], **kwargs: Any
    ) -> None:
        arg = {} if arg is None else arg
        super().__init__(CIMultiDict(arg, **kwargs))


class MutableHeaders(CIMultiDict[str]):
    pass
