from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Response:
    body: Any
    status_code: Optional[int] = None
    headers: Optional[dict[str, str]] = None

    @classmethod
    def from_tuple(cls, t):
        if len(t) == 1:
            return {"body": t[0]}
        elif len(t) == 2:
            return {"body": t[0], "statusCode": t[1]}
        elif len(t) == 3:
            return {"body": t[0], "statusCode": t[1], "headers": t[2]}

    @classmethod
    def from_any(cls, obj):
        if isinstance(obj, tuple):
            return cls.from_tuple(obj)
        return {"body": obj}

    def to_dict(self):
        result = {"body": self.body}
        if self.status_code is not None:
            result["statusCode"] = self.status_code

        if self.headers is not None:
            result["headers"] = self.headers

        return result


def make_response(resp: Any) -> dict[str, Any]:
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
