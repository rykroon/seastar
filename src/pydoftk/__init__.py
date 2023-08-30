from base64 import b64decode
from dataclasses import dataclass
from functools import cached_property
import json
from typing import Any
from urllib.parse import parse_qsl


@dataclass
class Request:
    method: str
    path: str
    query_string: str
    headers: dict[str, str]
    encoded_body: str
    is_base64_encoded: bool
    parameters: dict[str, Any]

    @classmethod
    def from_event(cls, event):
        http = event["http"]
        return cls(
            method=http["method"],
            path=http["path"],
            query_string=http["queryString"],
            headers=http["headers"],
            encoded_body=http["body"],
            is_base64_encoded=http["isBase64Encoded"],
            parameters={
                k: v
                for k, v in event.items()
                if not k.startswith("__ow") and k != "http"
            },
        )

    @cached_property
    def query_params(self):
        result = {}
        for k, v in parse_qsl(self.query_string):
            if k not in result:
                result[k] = v
            elif isinstance(result[k], list):
                result[k].append(v)
            else:
                result[k] = [result[k], v]

    @cached_property
    def content_type(self):
        return self.headers.get('content-type')

    @cached_property
    def body(self):
        return b64decode(self.encoded_body)

    @cached_property
    def json(self):
        if self.content_type != "application/json":
            return None
        return json.loads(self.body)

    @cached_property
    def form(self):
        if self.content_type != "":
            return None
        return ...


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
