from base64 import b64decode
from dataclasses import dataclass
import json
from typing import Any, Mapping
from typing_extensions import Self

from seastar.datastructures import Headers, QueryParams, FormData
from seastar.exceptions import HttpException
from seastar.types import Event


@dataclass
class Request:
    method: str
    path: str
    query_params: QueryParams[str, str]
    headers: Headers[str, str]
    body: str
    parameters: Mapping[str, str]

    @classmethod
    def from_event(cls: type[Self], event: Event) -> Self:
        assert "http" in event, "Expected a web event."
        http = event["http"]
        query_string = http.get("queryString", "")
        query_params = QueryParams.from_string(query_string)

        body = http.get("body", "")
        if http.get("isBase64Encoded", False):
            body = b64decode(body).decode()

        return cls(
            method=http["method"],
            path=http["path"],
            query_params=query_params,
            headers=http["headers"],
            body=body,
            parameters={
                k: v
                for k, v in event.items()
                if not k.startswith("__") and k not in ["http"]
            },
        )

    def json(self) -> Any:
        if self.headers.get("content-type") != "application/json":
            raise HttpException(415)

        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            raise HttpException(400)

    def form(self) -> FormData[str, str]:
        return FormData.from_string(self.body)
