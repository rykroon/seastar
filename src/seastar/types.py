import inspect
from typing import Any, Callable, Protocol, TypedDict, TYPE_CHECKING, Union
from typing_extensions import NotRequired, TypeAlias, TypeGuard


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
RequestHandler: TypeAlias = Callable[["Request"], "Response"]
Handler: TypeAlias = Union[EventHandler, RequestHandler]

ExceptionHandlerKey: TypeAlias = Union[int, type[Exception]]
EventExceptionHandler: TypeAlias = Callable[[Event, Context, Exception], HandlerResult]
RequestExceptionHandler: TypeAlias = Callable[["Request", Exception], "Response"]
ExceptionHandler: TypeAlias = Union[EventExceptionHandler, RequestExceptionHandler]


# type guards

def is_request_handler(func: Any) -> TypeGuard[RequestHandler]:
    sig = inspect.signature(func)
    if len(sig.parameters) != 1:
        return False
    
    parameters = list(sig.parameters.values())
    param = parameters[0]
    if not param.annotation is not inspect._empty:
        return param.annotation.__name__ == "Request"

    return param.name == "request"


def is_request_exception_handler(func: Any) -> TypeGuard[RequestExceptionHandler]:
    sig = inspect.signature(func)
    if len(sig.parameters) != 2:
        return False
    
    parameters = list(sig.parameters.values())
    param_one = parameters[0]

    if param_one.annotation is not inspect._empty:
        if param_one.annotation.__name__ != "Request":
            return False
    else:
        if param_one.name != "request":
            return False

    param_two = parameters[1]
    if param_two.annotation is not inspect._empty:
        if not issubclass(param_two.annotation, Exception):
            return False
    else:
        if param_two.name not in ("e", "exc", "exception"):
            return False
    
    return True
