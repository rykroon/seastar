from pydoftk import Request, function


def test_function_decorator():
    @function
    def my_function(request):
        assert isinstance(request, Request)
        return "Hello World"

    event = {
        "http": {
            "body": "",
            "headers": {},
            "method": "GET",
            "path": "",
            "queryString": "a=1",
        }
    }

    result = my_function(event)
    assert isinstance(result, dict)
    assert result["body"] == "Hello World"
