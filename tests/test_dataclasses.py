from dataclasses import dataclass
import typing

import pytest

from hosta_homework.dataclasses import FromDict

@dataclass
class SimpleDataclass(FromDict):
    foo: int
    bar: str


@dataclass
class NestedDataclass(FromDict):
    me: int
    child: SimpleDataclass


@dataclass
class CollectionDataclass(FromDict):
    foo: int
    strs: typing.List[str]
    dcs: typing.List[SimpleDataclass]


def test_flat():
    """A basic and not-interesting test to ensure basic deserialization works"""
    data = {
        "foo": 1234,
        "bar": "hello there"
        }

    dc = SimpleDataclass.from_dict(data)

    assert dc.foo == data["foo"]
    assert type(dc.foo) == type(data["foo"])
    assert dc.bar == data["bar"]
    assert type(dc.bar) == type(data["bar"])


def test_flat_overfull():
    """from_dict should also work in the event that there's extra stuff hanging out in the source data

    This is not behavior we would want in a fully-specified data model, but for this submission, I may
    desire to omit some fields for simplicity
    """
    data = {
        "foo": 1234,
        "bar": "hello there",
        "baz": "irrelevant"
        }

    dc = SimpleDataclass.from_dict(data)

    assert dc.foo == data["foo"]
    assert type(dc.foo) == type(data["foo"])
    assert dc.bar == data["bar"]
    assert type(dc.bar) == type(data["bar"])

    # The default constructor would have an issue with extra fields
    with pytest.raises(TypeError):
        SimpleDataclass(**data)


def test_nested():
    """This should _also_ create nested dataclasses"""
    data = {
        "me": 11111,
        "child": {
            "foo": 12345,
            "bar": "mmmmm",
            }
        }

    dc = NestedDataclass.from_dict(data)

    assert dc.me == data["me"]
    assert type(dc.me) == type(data["me"])
    assert type(dc.child) == SimpleDataclass

    assert dc.child.foo == data["child"]["foo"]
    assert type(dc.child.foo) == type(data["child"]["foo"])
    assert dc.child.bar == data["child"]["bar"]
    assert type(dc.child.bar) == type(data["child"]["bar"])


def test_collections():
    """This should _also_ create nested dataclasses"""
    data = {
        "foo": 12345,
        "strs": ["a", "b", "c"],
        "dcs": [
            {"foo": 1, "bar": "a"},
            {"foo": 2, "bar": "b"},
            {"foo": 3, "bar": "c"},
        ]
    }

    dc = CollectionDataclass.from_dict(data)
    assert dc.foo == data["foo"]
    assert dc.strs == data["strs"]
    assert type(dc.strs) == list
    assert type(dc.strs[0]) == str
    assert type(dc.dcs) == list
    assert type(dc.dcs[0]) == SimpleDataclass
    assert dc.dcs[0].foo == data["dcs"][0]["foo"]
    assert dc.dcs[0].bar == data["dcs"][0]["bar"]
    assert dc.dcs[1].foo == data["dcs"][1]["foo"]
    assert dc.dcs[1].bar == data["dcs"][1]["bar"]
    assert dc.dcs[2].foo == data["dcs"][2]["foo"]
    assert dc.dcs[2].bar == data["dcs"][2]["bar"]
