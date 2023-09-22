from seastar.exceptions import HttpException


class TestHttpException:
    def test_default_message(self):
        exc = HttpException(400)
        assert exc.detail == "Bad Request"
        assert exc.args == (400, "Bad Request")
    
    def test_custom_message(self):
        exc = HttpException(400, "Shit!")
        assert exc.detail == "Shit!"
        assert exc.args == (400, "Shit!")
