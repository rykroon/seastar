from seastar.handlers import debug_response, error_response


class TestDebugResponse:

    def test_web_event(self):
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        try:
            raise Exception("There was an error.")
        except Exception as exc:
            result = debug_response(event, None, exc)
            assert "Traceback" in result["body"]
            assert result["statusCode"] == 500

    def test_non_web_event(self):
        try:
            raise Exception("There was an error.")
        except Exception as exc:
            result = debug_response({}, None, exc)
            assert "Traceback" in result["body"]
            assert "statusCode" not in result
            assert "headers" not in result


class TestErrorResponse:

    def test_web_event(self):
        event = {"http": {"path": "", "method": "GET", "headers": {}}}
        try:
            raise Exception("There was an error.")
        except Exception as e:
            result = error_response(event, None, e)
            assert result["body"] == "Internal Server Error"
            assert result["statusCode"] == 500
            assert result["headers"]["content-type"] == "text/plain"

    def test_non_web_event(self):
        try:
            raise Exception("There was an error.")
        except Exception as e:
            result = error_response({}, None, e)
            assert result["body"] == "Internal Server Error"
            assert "statusCode" not in result
            assert "headers" not in result
