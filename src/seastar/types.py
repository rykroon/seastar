from typing import Any, Callable, Protocol, TYPE_CHECKING, Union

if TYPE_CHECKING:
    # avoids a circular import error.
    from seastar.requests import Request
    from seastar.responses import Response


Event = dict[str, Any]

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


App = Callable[[Event, Context], Any]
ExceptionHandlerKey = Union[int, type[Exception]]
ExceptionHandler = Callable[[Event, Context, Exception], Any]
HttpExceptionHandler = Callable[["Request", Exception], "Response"]
