from seastar import web_function
from seastar.responses import PlainTextResponse




def test_webfunction():

    @web_function()
    def handler(request):
        return PlainTextResponse("Hello World!")
    
    event = {"http": {"path": "", "method": "GET", "headers": {}}}

    result = handler(event, None)
    assert result["body"] == "Hello World!"
