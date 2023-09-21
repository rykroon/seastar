from dataclasses import dataclass
from http import HTTPStatus
from typing import Callable


@dataclass
class Route:
    path: str
    func: Callable
    methods: list[str]

    def __post_init__(self):
        # wrap function in RequestResponseMiddleware.
        ...

    def __call__(self, event, context):
        path_match, method_match = self.matches(event)
        if not path_match:
            return {"body": HTTPStatus(404).phrase, "statusCode": 404}

        if not method_match:
            return {"body": HTTPStatus(405).phrase, "statusCode": 405}

        return self.func(event, context)
    
    def matches(self, event) -> tuple[bool, bool]:
        path = event["http"]["path"]
        method = event["http"]["method"]
        return self.path == path, method in self.methods


@dataclass
class Router:
    routes: list[Route]

    def __call__(self, event, context):
        for route in self.routes:
            path_match, method_match = route.matches(event)
            if not path_match:
                continue

            if not method_match:
                return {"body": HTTPStatus(405).phrase, "statusCode": 405}

            break

        else:
            return {"body": HTTPStatus(404).phrase, "statusCode": 404}

        return route.func(event, context)

    def add_route(self, route: Route):
        self.routes.append(route)
