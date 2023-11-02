from typing import Any, Callable, Optional

from starlette.exceptions import HTTPException
from starlette.routing import (
    compile_path, get_name, BaseRoute as _BaseRoute, Match, Route as _Route
)

from seastar.requests import Request
from seastar.responses import PlainTextResponse
from seastar.types import Context, Event, EventHandler, HandlerResult, RequestHandler


def request_response(func: RequestHandler) -> EventHandler:
    def wrapper(event: Event, context: Context) -> HandlerResult:
        request = Request.from_event(event)
        response = func(request)
        return response()

    return wrapper


class BaseRoute(_BaseRoute):

    def matches(self, event: Event) -> tuple[Match, Event]:
        raise NotImplementedError
    
    def handler(self, event: Event, context: Context):
        raise NotImplementedError
    
    def __call__(self, event: Event, context: Context):
        match, child_event = self.matches(event)
        if match == Match.NONE:
            response = PlainTextResponse("Not Found", status_code=404)
            return response()

        event.update(child_event)
        return self.handle(event, context)
    

class Route(BaseRoute, _Route):
    
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        methods: Optional[list[str]] = None,
        name: Optional[str] = None,
        include_in_schema: bool = True,
    ) -> None:
        # assert path.startswith("/"), "Routed paths must start with '/'"
        self.path = path
        self.endpoint = endpoint
        self.name = get_name(endpoint) if name is None else name
        self.include_in_schema = include_in_schema

        if methods is None:
            self.methods = ["GET"]
        else:
            self.methods = [method.upper() for method in methods]

        self.app = request_response(endpoint)
        self.path_regex, self.path_format, self.param_convertors = compile_path(path)

    def matches(self, event: Event) -> tuple[Match, Event]:
        if "http" in event:
            match = self.path_regex.match(event["http"]["path"])
            if match:
                matched_params = match.groupdict()
                for key, value in matched_params.items():
                    matched_params[key] = self.param_convertors[key].convert(value)
                path_params = dict(event["http"].get("path_params", {}))
                path_params.update(matched_params)
                child_scope = {"endpoint": self.endpoint, "path_params": path_params}
                if self.methods and event["http"]["method"] not in self.methods:
                    return Match.PARTIAL, child_scope
                else:
                    return Match.FULL, child_scope
        return Match.NONE, {}
    
    def handle(self, event: Event, context: Context) -> None:
        if self.methods and event["http"]["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            if "app" not in event: # change this to entry_point??
                response = PlainTextResponse(
                    "Method Not Allowed", status_code=405, headers=headers
                )
                return response()

            raise HTTPException(status_code=405, headers=headers)

        else:
            return self.app(event, context)


# @dataclass
# class Route:
#     path: str
#     methods: list[str]
#     endpoint: InitVar[RequestHandler]
#     handler: EventHandler = field(init=False)

#     def __post_init__(
#         self, endpoint: RequestHandler
#     ) -> None:
#         if inspect.isfunction(endpoint) or inspect.ismethod(endpoint):
#             self.handler = request_response(endpoint)

#     def __call__(self, event: Event, context: Context) -> HandlerResult:
#         assert "http" in event, "Expected a web event."
#         is_entry_point = (
#             event.setdefault("__seastar", {}).setdefault("entry_point", self) is self
#         )

#         if self.path != event["http"]["path"]:
#             if not is_entry_point:
#                 raise HTTPException(404)

#             return {"body": "Not Found", "statusCode": 404}

#         if event["http"]["method"] not in self.methods:
#             headers = {"Allow": ", ".join(self.methods)}
#             if not is_entry_point:
#                 raise HTTPException(405, headers=headers)

#             return {"body": "Method Not Allowed", "statusCode": 405, "headers": headers}

#         return self.handler(event, context)

#     def matches(self, path: str, method: str) -> tuple[bool, bool]:
#         return path == self.path, method in self.methods


# @dataclass
# class Router:
#     routes: list[Route] = field(default_factory=list)

#     def __call__(self, event: Event, context: Context) -> HandlerResult:
#         assert "http" in event, "Expected a web event."
#         is_entry_point = (
#             event.setdefault("__seastar", {}).setdefault("entry_point", self) is self
#         )

#         path = event["http"]["path"]
#         method = event["http"]["method"]

#         for route in self.routes:
#             path_match, method_match = route.matches(path, method)
#             if not path_match:
#                 continue

#             if not method_match:
#                 headers = {"Allow": ", ".join(route.methods)}
#                 if not is_entry_point:
#                     raise HTTPException(405, headers=headers)

#                 return {
#                     "body": "Method Not Allowed",
#                     "statusCode": 405,
#                     "headers": headers,
#                 }

#             return route(event, context)

#         if not is_entry_point:
#             raise HTTPException(404)

#         return {"body": "Not Found", "statusCode": 404}

#     def add_route(
#         self, path: str, methods: list[str], endpoint: RequestHandler
#     ) -> None:
#         self.routes.append(Route(path, methods=methods, endpoint=endpoint))

