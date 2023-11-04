from seastar.responses import HTMLResponse, JSONResponse, PlainTextResponse


def test_html_response():
    response = HTMLResponse("Hello, World!")
    assert response.status_code == 200
    assert response.body == "Hello, World!"
    assert response.headers["content-type"] == "text/html; charset=utf-8"


def test_plain_text_response():
    response = PlainTextResponse("Hello, World!")
    assert response.status_code == 200
    assert response.body == "Hello, World!"
    assert response.headers["content-type"] == "text/plain; charset=utf-8"


def test_json_response():
    data = {"message": "Hello, World!"}
    response = JSONResponse(data)
    assert response.status_code == 200
    assert response.body == '{"message":"Hello, World!"}'
    assert response.headers["content-type"] == "application/json"

