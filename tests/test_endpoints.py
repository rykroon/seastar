import pytest

from seastar.endpoints import HttpEndpoint
from seastar.exceptions import HttpException
from seastar.responses import Response


@pytest.fixture
def get_event():
    return {
        "http": {
            "body": "",
            "headers": {},
            "method": "GET",
            "path": "",
            "queryString": "a=1",
        }
    }


@pytest.fixture
def post_event():
    return {
        "http": {
            "body": "",
            "headers": {},
            "method": "POST",
            "path": "",
            "queryString": "",
        }
    }


def test_endpoint(get_event, post_event):
    class MyEndpoint(HttpEndpoint):
        def get(self, request):
            return Response("Hello World")

    assert MyEndpoint().allowed_methods == ["GET"]
    assert MyEndpoint()(get_event, None) == {"body": "Hello World"}

    with pytest.raises(HttpException):
        MyEndpoint()(post_event, None)
