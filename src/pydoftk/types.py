from typing import Any, Callable

from pydoftk.requests import Request
from pydoftk.responses import Response


App = Callable[[dict[str, Any], dict[str, Any]], Any]
Endpoint = Callable[[Request], Response]
ExceptionHandler = Callable[[dict[str, Any], dict[str, Any], Exception], Any]
HttpExceptionHandler = Callable[[Request, Exception], Response]
