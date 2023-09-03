from base64 import b64decode
from dataclasses import dataclass
from functools import wraps
import json
from typing import Any, Optional
from urllib.parse import parse_qsl

from multidict import MultiDict, MultiDictProxy, CIMultiDict, CIMultiDictProxy


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query_params: MultiDictProxy[str, str]
    headers: CIMultiDictProxy[str, str]
    body: str
    parameters: dict[str, Any]

    @classmethod
    def from_event(cls, event):
        http = event["http"]
        query_params = MultiDictProxy(MultiDict(parse_qsl(http["queryString"])))
        headers = CIMultiDictProxy(CIMultiDict(http["headers"]))
        body = http["body"]
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

    def json(self) -> dict[str, Any]:
        return json.loads(self.body)

    def form(self) -> dict[str, Any]:
        return MultiDictProxy(MultiDict(parse_qsl(self.body)))


@dataclass
class Response:
    body: Any
    status_code: Optional[int] = None
    headers: Optional[dict[str, str]] = None


def function(func):
    @wraps(func)
    def wrapper(event):
        request = Request.from_event(event)
        try:
            result = func(request)

        except Exception as e:
            print(EXCEPTION_HANDLERS)
            for exc_class in type(e).mro()[:-2]:
                if exc_class in EXCEPTION_HANDLERS:
                    result = EXCEPTION_HANDLERS[exc_class](request, e)
                    break
            else:
                raise e

        return process_response(result)
    return wrapper


EXCEPTION_HANDLERS = {}


def error_handler(exc_class: type[Exception], /):
    def decorator(func):
        EXCEPTION_HANDLERS[exc_class] = func
        return func
    return decorator


def process_response(resp): # rename to make_response()
    if isinstance(resp, Response):
        result = {"body": resp.body}
        if resp.status_code is not None:
            result["statusCode"] = resp.status_code

        if resp.headers is not None:
            result["headers"] = resp.headers

        return result

    elif not isinstance(resp, tuple):
        return {"body": resp}

    if len(resp) == 1:
        return {"body": resp[0]}
    if len(resp) == 2:
        return {"body": resp[0], "statusCode": resp[1]}
    if len(resp) == 3:
        return {"body": resp[0], "statusCode": resp[1], "headers": resp[2]}
