from typing import Any, Callable, Protocol, TypedDict, TYPE_CHECKING, Union
from typing_extensions import NotRequired, TypeAlias


if TYPE_CHECKING:
    # avoids a circular import error.
    from seastar.requests import Request
    from seastar.responses import Response



class HttpDict(TypedDict):
    method: str
    path: str
    headers: dict[str, str]
    queryString: NotRequired[str]
    body: NotRequired[str]
    isBase64Encoded: NotRequired[bool]
    path_params: NotRequired[dict[str, str]]


class Event(TypedDict):
    http: NotRequired[HttpDict]
    __seastar: NotRequired[dict[str, Any]]


class WebEvent(TypedDict):
    http: HttpDict


class Context(Protocol):
    activation_id: str
    api_host: str
    api_key: str
    deadline: int
    function_name: str
    function_version: str
    namespace: str
    request_id: str

    def get_remaining_time_in_millis(self) -> int:
        pass


"""
    Notes on Digital Ocean Function result behavior.
    - if the function returns an object that is falsey, ex:
        - None
        - False
        - "" (empty string)
        - 0
        - Empty dict or list
         - A object whose __bool__ equates to False.
        ... then digital ocean returns an empty dictionary.
        However, if the object is NOT falsey then it MUST be a dictionary.
"""


JSON: TypeAlias = Union[dict[str, "JSON"], list["JSON"], str, int, float, bool, None]


class WebResult(TypedDict):
    body: NotRequired[JSON]
    statusCode: NotRequired[int]
    headers: NotRequired[dict[str, str]]


HandlerResult: TypeAlias = Union[WebResult, dict[str, JSON]]

EventHandler: TypeAlias = Callable[[Event, Context], HandlerResult]
WebHandler: TypeAlias = Callable[["Request"], "Response"]
Handler: TypeAlias = Union[EventHandler, WebHandler]

ExceptionHandlerKey: TypeAlias = Union[int, type[Exception]]
EventExceptionHandler: TypeAlias = Callable[[Event, Context, Exception], HandlerResult]
WebExceptionHandler: TypeAlias = Callable[["Request", Exception], "Response"]
ExceptionHandler: TypeAlias = Union[EventExceptionHandler, WebExceptionHandler]
