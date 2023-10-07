from typing import Any, Callable, Protocol, TypedDict, TYPE_CHECKING, Union
from typing_extensions import NotRequired, TypeAlias

if TYPE_CHECKING:
    # avoids a circular import error.
    from seastar.requests import Request
    from seastar.responses import Response


Event: TypeAlias = dict[str, Any]

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

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

class WebResult(TypedDict):
    body: NotRequired[JSON]
    statusCode: NotRequired[int]
    headers: NotRequired[dict[str, str]]

FunctionResult: TypeAlias = Union[WebResult, JSON]

EventHandler: TypeAlias = Callable[[Event, Context], FunctionResult]
WebEventHandler: TypeAlias = Callable[["Request"], "Response"]

ExceptionHandlerKey: TypeAlias = Union[int, type[Exception]]
EventExceptionHandler: TypeAlias = Callable[[Event, Context, Exception], FunctionResult]
WebEventExceptionHandler: TypeAlias = Callable[["Request", Exception], "Response"]
ExceptionHandler: TypeAlias = Union[EventExceptionHandler, WebEventExceptionHandler]
