from base64 import b64decode
from collections.abc import Mapping
from dataclasses import dataclass
import json
from typing import Any
from typing_extensions import Self
from urllib.parse import parse_qsl

from starlette.datastructures import QueryParams
from starlette.exceptions import HTTPException

from seastar.datastructures import Headers, FormData
from seastar.types import Event


@dataclass
class Request:
    method: str
    path: str
    query_params: QueryParams
    headers: Headers
    body: str
    parameters: Mapping[str, str]

    @classmethod
    def from_event(cls: type[Self], event: Event) -> Self:
        assert "http" in event, "Expected a web event."
        http = event["http"]
        query_string = http.get("queryString", "")
        query_params = QueryParams(query_string)

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
            raise HTTPException(415)

        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            raise HTTPException(400)

    def form(self) -> FormData:
        return FormData(parse_qsl(self.body))
