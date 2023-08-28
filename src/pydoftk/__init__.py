from dataclasses import dataclass
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


@dataclass
class Response:
    body: Any | None = None
    status_code: int | None = None
    headers: dict[str, str] | None = None


def process_response(resp):
    if isinstance(resp, Response):
        result = {}
        if resp.body is not None:
            result["body"] = resp.body

        if resp.status_code is not None:
            result["statusCode"] = resp.status_code

        if resp.headers is not None:
            result["headers"] = resp.headers

        return result or None

    elif not isinstance(resp, tuple):
        return {"body": resp}

    match len(resp):
        case 1:
            return {"body": resp[0]}
        case 2:
            return {"body": resp[0], "statusCode": resp[1]}
        case 3:
            return {"body": resp[0], "statusCode": resp[1], "headers": resp[2]}


def require_http_methods(method_list, /):
    def decorator(func):
        def wrapper(request):
            if request.method not in method_list:
                return "Method not allowed", 405
            return func(request)

        return wrapper

    return decorator


require_get = require_http_methods(["GET"])
require_post = require_http_methods(["POST"])
