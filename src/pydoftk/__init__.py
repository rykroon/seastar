from base64 import b64decode
from dataclasses import dataclass
from functools import wraps
import json
from typing import Any, Callable, Optional, TypeVar
from urllib.parse import parse_qsl

from multidict import MultiDict, MultiDictProxy, CIMultiDict, CIMultiDictProxy


Self = TypeVar("Self", bound="Request")


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query_params: MultiDictProxy[str]
    headers: CIMultiDictProxy[str]
    body: str
    parameters: dict[str, Any]

    @classmethod
    def from_event(cls: type[Self], event: dict[str, Any]) -> Self:
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

    def json(self) -> Any:
        return json.loads(self.body)

    def form(self) -> MultiDictProxy[Any]:
        return MultiDictProxy(MultiDict(parse_qsl(self.body)))


@dataclass
class Response:
    body: Any
    status_code: Optional[int] = None
    headers: Optional[dict[str, str]] = None


def function(
    func: Callable[[Request], Any]
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    @wraps(func)
    def wrapper(event: dict[str, Any]) -> dict[str, Any]:
        request = Request.from_event(event)
        try:
            result = func(request)

        except Exception as e:
            for exc_class in type(e).mro()[:-2]:
                if exc_class in EXCEPTION_HANDLERS:
                    result = EXCEPTION_HANDLERS[exc_class](request, e)
                    break
            else:
                raise e

        return process_response(result)

    return wrapper


EXCEPTION_HANDLERS = {}


def error_handler(
    exc_class: type[Exception], /
) -> Callable[[Callable[[Request, Exception], Any]], Any]:
    def decorator(func: Callable[[Request, Exception], Any]) -> Any:
        EXCEPTION_HANDLERS[exc_class] = func
        return func

    return decorator


def process_response(resp: Any) -> dict[str, Any]:  # rename to make_response()
    if isinstance(resp, Response):
        result = {"body": resp.body}
        if resp.status_code is not None:
            result["statusCode"] = resp.status_code

        if resp.headers is not None:
            result["headers"] = resp.headers

        return result

    elif isinstance(resp, tuple):
        if len(resp) == 1:
            return {"body": resp[0]}
        elif len(resp) == 2:
            return {"body": resp[0], "statusCode": resp[1]}
        elif len(resp) == 3:
            return {"body": resp[0], "statusCode": resp[1], "headers": resp[2]}

    return {"body": resp}
