import pytest

from seastar.datastructures import MultiDict, MutableMultiDict


@pytest.fixture
def list_() -> list[tuple]:
    return [("a", 1), ("b", 1), ("c", 1), ("a", 2), ("b", 2), ("a", 3)]


@pytest.fixture
def multidict(list_) -> MultiDict:
    return MultiDict(list_)


@pytest.fixture
def mutmultidict(list_) -> MutableMultiDict:
    return MutableMultiDict(list_)


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

    def test_getlist(self, multidict):
        assert multidict.getlist("a") == [1, 2, 3]

    def test_values(self, multidict, list_):
        assert list(multidict.values()) == list(dict(list_).values())
    
    def test_items(self, multidict, list_):
        assert list(multidict.items()) == list(dict(list_).items())
    
    def test_multi_items(self, multidict):
        assert list(multidict.multi_items()) == multidict._list
    
    def test_contains(self, multidict):
        assert "a" in multidict
        assert "d" not in multidict
    
    def test_iter(self, multidict, list_):
        assert list(iter(multidict)) == list(iter(dict(list_)))
    
    def test_len(self, multidict, list_):
        assert len(multidict) == len(dict(list_))
    
    def test_equality_success(self, multidict, list_):
        assert multidict == MultiDict(list_)

    def test_equality_fail(self, multidict, list_):
        assert multidict != dict(list_)


class TestMutableMultiDict:

    def test_setitem(self, mutmultidict):
        mutmultidict["d"] = 1
        assert mutmultidict["d"] == 1
    
    def test_delitem(self, mutmultidict):
        del mutmultidict["a"]
        assert "a" not in mutmultidict
    
    def test_pop(self, mutmultidict):
        a = mutmultidict.pop("a")
        assert a == 3
        assert "a" not in mutmultidict
    
    def test_popitem(self, mutmultidict):
        key, _ = mutmultidict.popitem()
        assert key not in mutmultidict
    
    def test_poplist(self, mutmultidict):
        assert mutmultidict.poplist("a") == [1, 2, 3]
        assert "a" not in mutmultidict
    
    def test_clear(self, mutmultidict):
        mutmultidict.clear()
        assert len(mutmultidict) == 0
    
    def test_setdefault(self, mutmultidict):
        assert mutmultidict.setdefault("d", 1) == 1
        assert mutmultidict.setdefault("d", 2) == 1
    
    def test_setlist_empty_list(self, mutmultidict):
        mutmultidict.setlist("a", [])
        assert "a" not in mutmultidict
    
    def test_append(self, mutmultidict):
        mutmultidict.append("a", 4)
        assert mutmultidict.getlist("a") == [1, 2, 3, 4]
    

