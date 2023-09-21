from dataclasses import dataclass
from typing import Optional, Union

from pydoftk.exceptions import HttpException
from pydoftk.types import Request, App, Handler


@dataclass
class ExceptionMiddleware:
    app: App
    exception_handlers: dict[Union[type[Exception], int], Handler]

    def __call__(self, event, context):
        try:
            return self.app(event, context)

        except Exception as e:
            handler = self.lookup_handler(e)
            if handler is None:
                raise e
            request = Request.from_event(event)
            response = handler(request, e)
            return response()

    def lookup_handler(self, exc: Exception) -> Optional[Handler]:
        if isinstance(exc, HttpException):
            if exc.status_code in self.exception_handlers:
                return self.exception_handlers[exc.status_code]

        for exc_class in type(exc).mro()[:-2]:
            if exc_class in self.exception_handlers:
                return self.exception_handlers[exc_class]

        return None
