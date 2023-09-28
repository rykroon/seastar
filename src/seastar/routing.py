from dataclasses import dataclass, field
from functools import wraps
from http import HTTPMethod
import inspect
from typing import Any

from .exceptions import HttpException
from .requests import Request
from .types import Event, Context, Endpoint


"""
    Routes are only applicable to web events.
"""


def request_response(func):
    @wraps(func)
    def wrapper(event: Event, context: Context):
        request = Request.from_event(event)
        response = func(request)
        return response()

    return wrapper


@dataclass(order=True)
class Route:
    path: str
    methods: list[HTTPMethod]
    endpoint: Endpoint

    def __post_init__(self):
        if inspect.isfunction(self.endpoint) or inspect.ismethod(self.endpoint):
            self.endpoint = request_response(self.endpoint)

    def __call__(self, event: Event, context: Context) -> Any:
        assert "http" in event, "Expected a web event."
        if self.path != event["http"]["path"]:
            raise HttpException(404)

        if event["http"]["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            raise HttpException(405, headers=headers)

        return self.endpoint(event, context)

    def matches(self, path: str, method: HTTPMethod):
        return path == self.path, method in self.methods


@dataclass
class Router:
    routes: list[Route] = field(default_factory=list)

    def __call__(self, event: Event, context: Context) -> Any:
        assert "http" in event, "Expected a web event."
        path = event["http"]["path"]
        method = event["http"]["method"]

        for route in self.routes:
            path_match, method_match = route.matches(path, method)
            if not path_match:
                continue

            if not method_match:
                headers = {"Allow": ", ".join(route.methods)}
                raise HttpException(405, headers=headers)

            return route.endpoint(event, context)

        raise HttpException(404)

    def add_route(self, route: Route):
        self.routes.append(route)
