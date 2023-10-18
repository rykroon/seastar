from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import uuid

from seastar.json import JsonEncoder


def test_dataclass():
    @dataclass
    class dclass:
        x: int

    o = dclass(x=1)
    assert json.dumps(o, cls=JsonEncoder) == '{"x": 1}'


def test_datetime():
    o = datetime(year=2023, month=1, day=1)
    assert json.dumps({"date": o}, cls=JsonEncoder) == '{"date": "2023-01-01T00:00:00"}'


def test_enum():
    class Foo(Enum):
        FOO = "foo"

    assert json.dumps({"enum": Foo.FOO}, cls=JsonEncoder) == '{"enum": "foo"}'


def test_uuid():
    o = uuid.UUID("cf7bbe5a-0886-4154-b24d-7d1b96626d3b")
    assert (
        json.dumps({"uuid": o}, cls=JsonEncoder)
        == '{"uuid": "cf7bbe5a-0886-4154-b24d-7d1b96626d3b"}'
    )


def test_other():
    d = {"a": True, "b": "two", "c": 3}
    assert json.dumps(d, cls=JsonEncoder) == '{"a": true, "b": "two", "c": 3}'