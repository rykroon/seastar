from base64 import b64decode
from dataclasses import dataclass
import json
from typing import Any, Optional, TypeVar

from seastar.datastructures import UrlFormEncodedDict, ImmutableCIMultiDict
Self = TypeVar("Self", bound="Request")


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query_params: UrlFormEncodedDict[str, str]
    headers: ImmutableCIMultiDict[str, str]
    body: str
    parameters: dict[str, Any]
    context: Optional[dict[str, Any]] = None

    @classmethod
    def from_event_context(
        cls: type[Self], event: dict[str, Any], context: Optional[dict[str, Any]] = None
    ) -> Self:
        assert "http" in event, "Expected a web event."
        http = event["http"]

        query_string = http.get("queryString", "")
        query_params = UrlFormEncodedDict.from_string(query_string)
        headers = ImmutableCIMultiDict(http["headers"])

        body = http.get("body", "")
        if http.get("isBase64Encoded", False):
            body = b64decode(body).decode()

        return cls(
            method=http["method"],
            path=http["path"],
            query_params=query_params,
            headers=headers,
            body=body,
            parameters={
                k: v
                for k, v in event.items()
                if not k.startswith("__ow") and k != "http"
            },
        )

    def json(self) -> Any:
        return json.loads(self.body)

    def form(self) -> UrlFormEncodedDict[str, str]:
        return UrlFormEncodedDict.from_string(self.body)
