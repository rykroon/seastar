from dataclasses import dataclass
from typing import Any, Optional, TypeVar, Union


Self = TypeVar("Self", bound="Response")


@dataclass
class Response:
    body: Any
    status_code: Optional[int] = None
    headers: Optional[dict[str, str]] = None

    @classmethod
    def from_tuple(
        cls: type[Self],
        t: Union[tuple[Any], tuple[Any, int], tuple[Any, int, dict[str, Any]]]
    ) -> Self:
        if len(t) == 1:
            return cls(body=t[0])
        elif len(t) == 2:
            return cls(body=t[0], status_code=t[1])
        elif len(t) == 3:
            return cls(body=t[0], status_code=t[1], headers=t[2])
        # handle tuple of length 0 and greater than 3

    @classmethod
    def from_any(cls: type[Self], obj: Any) -> Self:
        if isinstance(obj, tuple):
            return cls.from_tuple(obj)
        return cls(body=obj)

    def to_dict(self: Self) -> dict[str, Any]:
        result = {"body": self.body}
        if self.status_code is not None:
            result["statusCode"] = self.status_code

        if self.headers is not None:
            result["headers"] = self.headers

        return result
