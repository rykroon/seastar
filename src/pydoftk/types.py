from typing import Any, Callable, Optional

from pydoftk.requests import Request
from pydoftk.responses import Response


App = Callable[[dict[str, Any], dict[str, Any]], Any]
Handler = Callable[[Request, Exception], Response]
