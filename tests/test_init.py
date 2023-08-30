from base64 import b64encode

from pydoftk import process_response, ParsedWebEvent, RawWebEvent, Response


def test_parsed_web_event():
    event_data = {
        "__ow_headers": None,
        "__ow_method": None,
        "__ow_path": None,
        "http": {
            "headers": {"content-type": "application/json"},
            "method": "GET",
            "path": "/path",
        },
        "foo": "bar",
    }

    event = ParsedWebEvent.from_event(event_data)

    assert event.headers == event_data["http"]["headers"]
    assert event.method == event_data["http"]["method"]
    assert event.path == event_data["http"]["path"]
    assert event.data == {"foo": "bar"}


def test_raw_web_event():
    encoded_body = b64encode(b"hello world")

    event_data = {
        "__ow_headers": None,
        "__ow_method": None,
        "__ow_path": None,
        "http": {
            "body": encoded_body,
            "headers": {"content-type": "application/json"},
            "isBase64Encoded": True,
            "method": "GET",
            "path": "/path",
            "queryString": "a=1",
        },
        "foo": "bar",
    }

    event = RawWebEvent.from_event(event_data)

    assert event.body == event_data["http"]["body"]
    assert event.headers == event_data["http"]["headers"]
    assert event.is_base64_encoded == event_data["http"]["isBase64Encoded"]
    assert event.method == event_data["http"]["method"]
    assert event.path == event_data["http"]["path"]
    assert event.query_string == event_data["http"]["queryString"]
    assert event.parameters == {"foo": "bar"}

    assert event.content_type == "application/json"
    assert event.query_params == {"a": ["1"]}
    assert event.decoded_body == b"hello world"


class TestProcessResponse:
    def test_any(self):
        assert process_response("Hello World") == {"body": "Hello World"}

    def test_response_body(self):
        result = Response("Hello World")
        assert process_response(result) == {"body": "Hello World"}
    
    def test_response_status_code(self):
        result = Response("Hello World", status_code=200)
        assert process_response(result) == {"body": "Hello World", "statusCode": 200}
    
    def test_response_headers(self):
        result = Response("Hello World", status_code=200, headers={"foo": "bar"})
        assert process_response(result) == {
            "body": "Hello World",
            "statusCode": 200,
            "headers": {"foo": "bar"},
        }

    def test_one_tuple(self):
        result = ("Hello World",)
        assert process_response(result) == {"body": "Hello World"}

    def test_two_tuple(self):
        result = ("Hello World", 200)
        assert process_response(result) == {"body": "Hello World", "statusCode": 200}

    def test_three_tuple(self):
        result = ("Hello World", 200, {"foo": "bar"})
        assert process_response(result) == {
            "body": "Hello World",
            "statusCode": 200,
            "headers": {"foo": "bar"},
        }
