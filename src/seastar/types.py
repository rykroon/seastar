from typing import Any, Callable

from seastar.requests import Request
from seastar.responses import Response


App = Callable[[dict[str, Any], dict[str, Any]], Any]
Endpoint = Callable[[Request], Response]
ExceptionHandler = Callable[[dict[str, Any], dict[str, Any], Exception], Any]
HttpExceptionHandler = Callable[[Request, Exception], Response]
