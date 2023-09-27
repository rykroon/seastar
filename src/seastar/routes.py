from dataclasses import dataclass, field
from functools import wraps
import inspect
from typing import Callable

from .exceptions import HttpException
from .requests import Request


"""
    Routes are only applicable to web events.
"""


def request_response(func):
    @wraps(func)
    def wrapper(event, context):
        request = Request.from_event_context(event, context)
        response = func(request)
        return response()

    return wrapper


@dataclass(order=True)
class Route:
    path: str
    methods: list[str]
    endpoint: Callable

    def __post_init__(self):
        if inspect.isfunction(self.endpoint) or inspect.ismethod(self.endpoint):
            self.endpoint = request_response(self.endpoint)

    def __call__(self, event, context):
        assert "http" in event, "Expected a web event."
        if self.path != event["http"]["path"]:
            raise HttpException(404)

        if event["http"]["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            raise HttpException(405, headers=headers)

        return self.endpoint(event, context)

    def matches(self, path: str, method: str):
        return path == self.path, method in self.methods


@dataclass
class Router:
    routes: list[Route] = field(default_factory=list)

    def __call__(self, event, context):
        assert "http" in event, "Expected a web event."
        path = event["http"]["path"]
        method = event["http"]["method"]

        status_code = 404
        headers = {}
        for route in self.routes:
            if path != route.path:
                continue

            if method not in route.methods:
                headers["Allow"] = ", ".join(route.methods)
                status_code = 405
                continue

            break

        else:
            raise HttpException(status_code, headers=headers)

        return route.endpoint(event, context)

    def add_route(self, route: Route):
        self.routes.append(route)
