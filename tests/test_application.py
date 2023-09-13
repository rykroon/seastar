from pydoftk import Application, Route

import pytest

@pytest.fixture
def event():
    return {
        "http": {
            "body": "",
            "headers": {},
            "method": "GET",
            "path": "",
            "queryString": "a=1",
        }
    }


class TestApplication:

    def test_app(self, event):
        app = Application()

        @app.route("", methods=["GET", "POST"])
        def func(request):
            return "OK", 200

        resp = app(event)
        assert resp == {"body": "OK", "statusCode": 200}

    def test_not_found(self, event):
        app = Application()
        resp = app(event)
        assert resp == {"body": "Not Found", "statusCode": 404}

    def test_method_not_allowed(self, event):
        app = Application()

        @app.route("", methods=["POST"])
        def func(request):
            return "OK", 200

        resp = app(event)
        assert resp == {"body": "Method Not Allowed", "statusCode": 405}
    
    def test_get_route(self):
        app = Application()

        @app.get("")
        def func(request):
            return "OK", 200
        
        assert app.routes == [Route("", func, ["GET"])]

    def test_post_route(self):
        app = Application()

        @app.post("")
        def func(request):
            return "OK", 200

        assert app.routes == [Route("", func, ["POST"])]
