from base64 import b64decode
from dataclasses import dataclass
from functools import cached_property
import json
from typing import Any
from urllib.parse import parse_qsl
from multidict import MultiDict, MultiDictProxy


@dataclass
class Request:
    method: str
    path: str
    query_string: str
    headers: dict[str, str]
    body: str
    parameters: dict[str, Any]

    @classmethod
    def from_event(cls, event):
        http = event["http"]
        body = http["body"]
        if http.get("isBase64Encoded", False):
            body = b64decode(body)

        return cls(
            method=http["method"],
            path=http["path"],
            query_string=http["queryString"],
            headers=http["headers"],
            body=body,
            parameters={
                k: v
                for k, v in event.items()
                if not k.startswith("__ow") and k != "http"
            },
        )

    @cached_property
    def query_params(self):
        return MultiDictProxy(MultiDict(parse_qsl(self.query_string)))

    @cached_property
    def content_type(self):
        return self.headers.get("content-type")

    def json(self):
        return json.loads(self.body)

    def form(self):
        return MultiDictProxy(MultiDict(parse_qsl(self.body)))


@dataclass
class Response:
    body: Any
    status_code: int | None = None
    headers: dict[str, str] | None = None


def function(func):
    def wrapper(event):
        request = Request.from_event(event)
        result = func(request)
        return process_response(result)

    return wrapper


def process_response(resp):
    if isinstance(resp, Response):
        result = {"body": resp.body}
        if resp.status_code is not None:
            result["statusCode"] = resp.status_code

        if resp.headers is not None:
            result["headers"] = resp.headers

        return result

    elif not isinstance(resp, tuple):
        return {"body": resp}

    match len(resp):
        case 1:
            return {"body": resp[0]}
        case 2:
            return {"body": resp[0], "statusCode": resp[1]}
        case 3:
            return {"body": resp[0], "statusCode": resp[1], "headers": resp[2]}
