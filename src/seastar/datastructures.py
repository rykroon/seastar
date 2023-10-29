from collections.abc import ItemsView, Iterator, KeysView, Mapping, Sequence, ValuesView
from urllib.parse import parse_qsl, urlencode
from typing import Any, Optional, TypeVar, Union

from typing_extensions import Self


K = TypeVar("K")
V = TypeVar("V")


class MultiDict(Mapping[K, V]):
    _list: list[tuple[K, V]]
    _dict: dict[K, V]

    def __init__(
        self,
        arg: Union[Mapping[K, V], Sequence[tuple[K, V]], None] = None,
    ):
        self._list = []

        if arg is not None:
            itty = arg.items() if isinstance(arg, Mapping) else arg
            self._list.extend(itty)

        self._dict = dict(self._list)

    def getlist(self, key: K) -> list[V]:
        return [item_value for item_key, item_value in self._list if item_key == key]

    def keys(self) -> KeysView[K]:
        return self._dict.keys()

    def values(self) -> ValuesView[V]:
        return self._dict.values()

    def items(self) -> ItemsView[K, V]:
        return self._dict.items()

    def multi_items(self) -> list[tuple[K, V]]:
        return list(self._list)

    def __getitem__(self, key: K) -> V:
        return self._dict[key]

    def __contains__(self, key: Any) -> bool:
        return key in self._dict

    def __iter__(self) -> Iterator[K]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._dict)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return sorted(self._list) == sorted(other._list)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        items = self.multi_items()
        return f"{class_name}({items!r})"


class MutableMultiDict(MultiDict[K, V]):
    def __setitem__(self, key: K, value: V) -> None:
        self.setlist(key, [value])

    def __delitem__(self, key: K) -> None:
        self._list = [(k, v) for k, v in self._list if k != key]
        del self._dict[key]

    def pop(self, key: K, default: Optional[V] = None) -> Any:
        self._list = [(k, v) for k, v in self._list if k != key]
        return self._dict.pop(key, default)

    def popitem(self) -> tuple[K, V]:
        key, value = self._dict.popitem()
        self._list = [(k, v) for k, v in self._list if k != key]
        return key, value

    def poplist(self, key: K) -> list[V]:
        values = [v for k, v in self._list if k == key]
        self.pop(key)
        return values

    def clear(self) -> None:
        self._dict.clear()
        self._list.clear()

    def setdefault(self, key: K, default: V) -> V:
        if key not in self:
            self._dict[key] = default
            self._list.append((key, default))

        return self[key]

    def setlist(self, key: K, values: list[V]) -> None:
        if not values:
            self.pop(key, None)
        else:
            existing_items = [(k, v) for (k, v) in self._list if k != key]
            self._list = existing_items + [(key, value) for value in values]
            self._dict[key] = values[-1]

    def append(self, key: K, value: V) -> None:
        self._list.append((key, value))
        self._dict[key] = value

    def update(
        self,
        arg: Union[
            Mapping[K, V],
            Sequence[tuple[K, V]],
        ],
        **kwargs: Any,
    ) -> None:
        value = MultiDict(arg, **kwargs)
        existing_items = [(k, v) for (k, v) in self._list if k not in value.keys()]
        self._list = existing_items + value.multi_items()
        self._dict.update(value)


class UrlFormEncodedDict(MultiDict[str, str]):
    def __str__(self) -> str:
        return urlencode(self._list)

    @classmethod
    def from_string(cls, s: str, /) -> Self:
        return cls(parse_qsl(s))


class QueryParams(UrlFormEncodedDict):
    pass


class FormData(UrlFormEncodedDict):
    pass


class Headers(MultiDict[str, str]):
    def __init__(
        self,
        arg: Union[Mapping[str, str], Sequence[tuple[str, str]], None] = None,
        **kwargs: str,
    ):
        super().__init__(arg, **kwargs)
        self._list = [(k.lower(), v) for k, v in self._list]
        self._dict = {k.lower(): v for k, v in self._dict.items()}

    def getlist(self, key: str) -> list[str]:
        return super().getlist(key.lower())

    def __getitem__(self, key: str) -> str:
        return super().__getitem__(key.lower())

    def __contains__(self, key: Any) -> bool:
        return super().__contains__(key.lower())


class MutableHeaders(Headers, MutableMultiDict[str, str]):
    def __setitem__(self, key: str, value: str) -> None:
        super().__setitem__(key.lower(), value)

    def __delitem__(self, key: str) -> None:
        super().__delitem__(key.lower())

    def setdefault(self, key: str, value: str) -> str:
        return super().setdefault(key.lower(), value)

    def append(self, key: str, value: str) -> None:
        super().append(key.lower(), value)
