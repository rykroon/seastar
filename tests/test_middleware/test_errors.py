
from seastar.middleware.errors import ServerErrorMiddleware

def test_debug_response():
    def app(event, context):
        raise Exception("There was an error.")
    
    mw = ServerErrorMiddleware(app, debug=True)

    result = mw({}, None)
    assert "There was an error" in result["body"]
    assert result["statusCode"] == 500


def test_error_response():
    def app(event, context):
        raise Exception("There was an error.")

    mw = ServerErrorMiddleware(app)
    result = mw({}, None)
    assert result["body"] == "Internal Server Error"
    assert result["statusCode"] == 500


def test_custom_error_handler():
    def app(event, context):
        raise Exception("There was an error.")
    
    def error_handler(event, context, e):
        return {"body": "Custom error response."}
    
    mw = ServerErrorMiddleware(app, handler=error_handler)
    result = mw({}, None)
    assert result["body"] == "Custom error response."
