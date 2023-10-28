from collections.abc import ItemsView, Iterator, KeysView, Mapping, ValuesView
from urllib.parse import parse_qsl, urlencode
from typing import Any, TypeVar, Union

from typing_extensions import Self


K = TypeVar("K")
V = TypeVar("V")


class MultiDict(Mapping[K, V]):

    _list: list[tuple[K, V]]
    _dict: dict[K, V]

    def __init__(
        self,
        arg: Union[Mapping[K, V], list[tuple[K, V]], None] = None,
        /,
        **kwargs: V
    ):
        self._list = []

        if arg is not None:
            itty = arg.items() if isinstance(arg, Mapping) else arg
            self._list.extend(itty)

        if kwargs:
            self._list.extend(kwargs.items())

        self._dict = dict(self._list)

    def getlist(self, key: Any) -> list[V]:
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


class MutableMultiDict(MultiDict):

    def __setitem__(self, key: Any, value: Any) -> None:
        self.setlist(key, [value])

    def __delitem__(self, key: Any) -> None:
        self._list = [(k, v) for k, v in self._list if k != key]
        del self._dict[key]

    def pop(self, key: Any, default: Any = None) -> Any:
        self._list = [(k, v) for k, v in self._list if k != key]
        return self._dict.pop(key, default)

    def popitem(self) -> tuple[Any, Any]:
        key, value = self._dict.popitem()
        self._list = [(k, v) for k, v in self._list if k != key]
        return key, value

    def poplist(self, key: Any) -> list[Any]:
        values = [v for k, v in self._list if k == key]
        self.pop(key)
        return values

    def clear(self) -> None:
        self._dict.clear()
        self._list.clear()

    def setdefault(self, key: Any, default: Any = None) -> Any:
        if key not in self:
            self._dict[key] = default
            self._list.append((key, default))

        return self[key]

    def setlist(self, key: Any, values: list[Any]) -> None:
        if not values:
            self.pop(key, None)
        else:
            existing_items = [(k, v) for (k, v) in self._list if k != key]
            self._list = existing_items + [(key, value) for value in values]
            self._dict[key] = values[-1]

    def append(self, key: Any, value: Any) -> None:
        self._list.append((key, value))
        self._dict[key] = value

    def update(
        self,
        arg: Union[Mapping[Any, Any], list[tuple[Any, Any]],],
        **kwargs: Any,
    ) -> None:
        value = MultiDict(arg, **kwargs)
        existing_items = [(k, v) for (k, v) in self._list if k not in value.keys()]
        self._list = existing_items + value.multi_items()
        self._dict.update(value)


class UrlFormEncodedDict(MultiDict[str, str]):

    def __str__(self):
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
        arg: Union[Mapping[str, str], list[tuple[str, str]], None] = None,
        **kwargs: str
    ):
        super().__init__(arg, **kwargs)
        self._list = [(k.lower(), v) for k, v in self._list]
        self._dict = {k.lower(): v for k, v in self._dict.items()}

    def getlist(self, key: str):
        super().getlist(key.lower())

    def __getitem__(self, key: str):
        super().__getitem__(key.lower())
    
    def __contains__(self, key: str):
        return super().__contains__(key.lower())


class MutableHeaders(Headers, MutableMultiDict):
    
    def __setitem__(self, key: str, value: str) -> None:
        super().__setitem__(key.lower(), value)
    
    def __delitem__(self, key: str) -> None:
        super().__delitem__(key.lower())
    
    def setdefault(self, key: str, value: str):
        super().setdefault(key.lower(), value)
    
    def append(self, key: str, value: str) -> None:
        super().append(key.lower(), value)
