from base64 import b64decode
from dataclasses import dataclass
import json
from urllib.parse import parse_qsl
from typing import Any, Optional, TypeVar

from multidict import MultiDict, MultiDictProxy, CIMultiDict, CIMultiDictProxy

Self = TypeVar("Self", bound="Request")


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query_params: MultiDictProxy[str]
    headers: CIMultiDictProxy[str]
    _body: str
    _is_base64_encoded: bool
    parameters: dict[str, Any]
    context: Optional[dict[str, Any]] = None

    @classmethod
    def from_event_context(
        cls: type[Self], event: dict[str, Any], context: Optional[dict[str, Any]] = None
    ) -> Self:
        assert "http" in event
        http = event["http"]
        query_params = MultiDictProxy(MultiDict(parse_qsl(http["queryString"])))
        headers = CIMultiDictProxy(CIMultiDict(http["headers"]))

        return cls(
            method=http["method"],
            path=http["path"],
            query_params=query_params,
            headers=headers,
            _body=http["body"],
            _is_base64_encoded=http.get("isBase64Encoded", False),
            parameters={
                k: v
                for k, v in event.items()
                if not k.startswith("__ow") and k != "http"
            },
            context=context,
        )

    def body(self):
        if not self._is_base64_encoded:
            return self._body
        return b64decode(self._body).decode()

    def json(self) -> Any:
        return json.loads(self.body())

    def form(self) -> MultiDictProxy[Any]:
        return MultiDictProxy(MultiDict(parse_qsl(self.body())))
