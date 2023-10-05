from seastar.handlers import debug_response, error_response


class TestDebugResponse:

    def test_web_event(self):
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        try:
            raise Exception("There was an error.")
        except Exception as exc:
            result = debug_response(event, None, exc)
            assert isinstance(result, dict)
            assert result["statusCode"] == 500
            assert "Traceback" in result["body"]

    def test_non_web_event(self):
        try:
            raise Exception("There was an error.")
        except Exception as exc:
            result = debug_response({}, None, exc)
            assert isinstance(result, str)
            assert "Traceback" in result


class TestErrorResponse:

    def test_web_event(self):
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        try:
            raise Exception("There was an error.")
        except Exception as e:
            result = error_response(event, None, e)
            assert isinstance(result, dict)
            assert result["statusCode"] == 500
            assert result["body"] == "Internal Server Error"
            assert result["headers"]["content-type"] == "text/plain"

    def test_non_web_event(self):
        try:
            raise Exception("There was an error.")
        except Exception as e:
            result = error_response({}, None, e)
            assert isinstance(result, str)
            assert result == "Internal Server Error"
