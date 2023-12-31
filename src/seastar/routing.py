from typing import Any, Optional

from starlette.exceptions import HTTPException
from starlette.routing import compile_path, get_name, Match

from seastar.exceptions import WebEventException
from seastar.requests import Request
from seastar.responses import PlainTextResponse
from seastar.types import Context, Event, EventHandler, HandlerResult, WebHandler


def request_response(func: WebHandler) -> EventHandler:
    def wrapper(event: Event, context: Context) -> HandlerResult:
        request = Request(event)
        response = func(request)
        return response()

    return wrapper


class Route:
    def __init__(
        self,
        path: str,
        endpoint: WebHandler,
        *,
        methods: Optional[list[str]] = None,
        name: Optional[str] = None,
    ) -> None:
        # assert path.startswith("/"), "Routed paths must start with '/'"
        self.path = path
        self.endpoint = endpoint
        self.name = get_name(endpoint) if name is None else name

        if methods is None:
            self.methods = {"GET"}
        else:
            self.methods = {method.upper() for method in methods}

        self.app = request_response(endpoint)
        self.path_regex, self.path_format, self.param_convertors = compile_path(path)

    def __call__(self, event: Event, context: Context) -> HandlerResult:
        if "http" not in event:
            raise WebEventException("The event was expected to be a web event.")

        _ = event.setdefault("__seastar", {}).setdefault("entry_point", self) is self

        match, path_params = self.matches(event)
        if match == Match.NONE:
            response = PlainTextResponse("Not Found", status_code=404)
            return response()

        event["http"].setdefault("path_params", path_params)
        return self.handle(event, context)

    def matches(self, event: Event) -> tuple[Match, dict[str, Any]]:
        match = self.path_regex.match(event["http"]["path"])
        if not match:
            return Match.NONE, {}

        matched_params = match.groupdict()
        for key, value in matched_params.items():
            matched_params[key] = self.param_convertors[key].convert(value)

        path_params = dict(event["http"].get("path_params", {}))
        path_params.update(matched_params)

        if self.methods and event["http"]["method"] not in self.methods:
            return Match.PARTIAL, path_params

        return Match.FULL, path_params

    def handle(self, event: Event, context: Context) -> HandlerResult:
        assert "http" in event, "Event is not a web event."

        if event["http"]["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            is_entry_point = event.get("__seastar", {}).get("entry_point") is self

            if is_entry_point:
                response = PlainTextResponse(
                    "Method Not Allowed", status_code=405, headers=headers
                )
                return response()

            raise HTTPException(status_code=405, headers=headers)

        return self.app(event, context)
