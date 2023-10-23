import pytest

from seastar.datastructures import MultiDict


@pytest.fixture
def list_():
    return [("a", 1), ("b", 1), ("c", 1), ("a", 2), ("b", 2), ("a", 3)]


class TestMultiDict:

    def test_init_arg_is_list(self, list_):
        md = MultiDict(list_)
        assert md._list == list_
        assert md._dict == dict(list_)
    
    def test_init_arg_is_mapping(self):
        dct = {"a": 1, "b": 1}
        md = MultiDict(dct)
        assert md._dict == dct
        assert md._list == list(dct.items())

    def test_init_kwargs(self):
        md = MultiDict(a=1, b=1)
        assert md._dict == {"a": 1, "b": 1}
        assert md._list == [("a", 1), ("b", 1)]
    
    def test_getlist(self, list_):
        md = MultiDict(list_)
        assert md.getlist("a") == [1, 2, 3]

    def test_values(self, list_):
        md = MultiDict(list_)
        assert list(md.values()) == list(dict(list_).values())
    
    def test_items(self, list_):
        md = MultiDict(list_)
        assert list(md.items()) == list(dict(list_).items())
    
    def test_multi_items(self, list_):
        md = MultiDict(list_)
        assert list(md.multi_items()) == md._list
    
    def test_contains(self, list_):
        md = MultiDict(list_)
        assert "a" in md
        assert "d" not in md
    
    def test_iter(self, list_):
        md = MultiDict(list_)
        assert list(iter(md)) == list(iter(dict(list_)))
    
    def test_len(self, list_):
        md = MultiDict(list_)
        assert len(md) == len(dict(list_))
    

