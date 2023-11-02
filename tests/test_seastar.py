from seastar import web_function
from seastar.responses import PlainTextResponse




def test_webfunction():

    @web_function()
    def handler(request):
        return PlainTextResponse("Hello World!")
    
    event = {"http": {"path": "", "method": "GET", "headers": {}}}

    result = handler(event, None)
    assert result["body"] == "Hello World!"


def test_webfunction_with_errorhandlers():

    @web_function()
    def event_handler(request):
        raise RuntimeError("shit!")
    
    def error_handler(event, context, exc):
        return {"body": str(exc)}

    event_handler.add_exception_handler(RuntimeError, error_handler)
    event = {"http": {"path": "", "method": "GET", "headers": {}}}
    result = event_handler(event, None)
    assert result["body"] == "shit!"

