from starlette.exceptions import HTTPException


class TestHttpException:
    def test_default_message(self):
        exc = HTTPException(400)
        assert exc.detail == "Bad Request"
        assert exc.args == (400, "Bad Request")

    def test_custom_message(self):
        exc = HTTPException(400, "Shit!")
        assert exc.detail == "Shit!"
        assert exc.args == (400, "Shit!")

    def test_str(self):
        assert str(HTTPException(400)) == "400: Bad Request"
