from seastar.handlers import debug_response, error_response


def test_debug_response():
    try:
        raise Exception("There was an error.")
    except Exception as exc:
        response = debug_response({}, None, exc)
        result = response()
        assert result["statusCode"] == 500
        assert "Traceback" in result["body"]


def test_error_response():    
    exc = Exception("There was an error.")

    result = error_response({}, None, exc)
    assert result["statusCode"] == 500
    assert result["body"] == "Internal Server Error"
    assert result["headers"]["content-type"] == "text/plain"
