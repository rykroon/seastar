from base64 import b64decode
import json
from typing import Any, Mapping
from typing_extensions import Self

from seastar.datastructures import Headers, QueryParams, FormData
from seastar.exceptions import HttpException
from seastar.types import Event


class Request:

    def __init__(
        self,
        method: str,
        path: str,
        query_params: Mapping[str, str],
        headers: Mapping[str, str],
        body: str,
        parameters: Mapping[str, str]
    ) -> None:
        if not isinstance(query_params, QueryParams):
            query_params = QueryParams(query_params)

        if not isinstance(headers, Headers):
            headers = Headers(headers)

        self.method = method
        self.path = path
        self.query_params = QueryParams(query_params)
        self.headers = headers
        self.body = body
        self.parameters = parameters

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
                if not k.startswith("__ow") and k not in ["http"]
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
