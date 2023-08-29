from base64 import b64decode
from dataclasses import dataclass
from functools import cached_property
from typing import Any


@dataclass
class ParsedWebEvent:
    """
    https://docs.digitalocean.com/products/functions/reference/parameters-responses/#parsed-web-events
    """
    headers: dict[str, str]
    method: str
    path: str
    data: dict[str, Any]

    @classmethod
    def from_event(cls, event):
        http = event["http"]
        return cls(
            headers=http["headers"],
            method=http["method"],
            path=http["path"],
            data={
                k: v
                for k, v in event.items()
                if not k.startswith("__ow") and k != "http"
            },
        )


@dataclass
class RawWebEvent:
    """
    https://docs.digitalocean.com/products/functions/reference/parameters-responses/#raw-web-events
    """
    body: str
    headers: dict[str, str]
    is_base64_encoded: bool
    method: str
    path: str
    query_string: str
    parameters: dict[str, Any]

    @classmethod
    def from_event(cls, event):
        http = event["http"]
        return cls(
            headers=http["headers"],
            method=http["method"],
            path=http["path"],
            body=http["body"],
            is_base64_encoded=http["isBase64Encoded"],
            query_string=http["queryString"],
            parameters={
                k: v
                for k, v in event.items()
                if not k.startswith("__ow") and k != "http"
            },
        )

    @cached_property
    def decoded_body(self):
        return b64decode(self.body)

    @cached_property
    def content_type(self):
        return self.headers.get('content-type')


@dataclass
class Response:
    body: Any | None = None
    status_code: int | None = None
    headers: dict[str, str] | None = None


def function(methods=None, raw=False):
    if methods is None:
        methods = ["GET"]

    # add logic for parsing path parameters.

    def decorator(func):
        def wrapper(event):
            if not raw:
                request = ParsedWebEvent.from_event(event)
            else:
                request = RawWebEvent.from_event(event)
            
            # add logic to consider passing in the context variable.
            # may require using inspect.signature.

            if request.method not in methods:
                resp = "Method Not Allowed", 405
                return process_response(resp)
            
            response = func(request)
            return process_response(response)
        return wrapper
    return decorator


def process_response(resp):
    if isinstance(resp, Response):
        result = {}
        if resp.body is not None:
            result["body"] = resp.body

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
