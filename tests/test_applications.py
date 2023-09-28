

from seastar import SeaStar


class TestApplication:

    def test_route_not_found(self):
        event = {
            "http": {
                "body": "",
                "headers": {},
                "method": "GET",
                "path": "",
                "queryString": "a=1&b=2",
            }
        }
        app = SeaStar()
        assert app(event, None) == {
            "body": "Not Found",
            "statusCode": 404,
            "headers": {"content-type": "text/plain"}
        }
