from seastar.exceptions import HttpException


class TestHttpException:
    def test_default_message(self):
        exc = HttpException(400)
        assert exc.message == "Bad Request"
        assert exc.args == (400, "Bad Request")
    
    def test_custom_message(self):
        exc = HttpException(400, "Shit!")
        assert exc.message == "Shit!"
        assert exc.args == (400, "Shit!")
