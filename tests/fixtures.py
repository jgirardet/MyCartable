from itertools import zip_longest
from operator import itemgetter, attrgetter
from unittest.mock import patch, MagicMock

from pony.orm import db_session
from contextlib import contextmanager


def compare_items(first, two, key="id"):
    for x, y in zip(first, two):
        assert getattr(x, key) == getattr(y,key)

def compare(first, two, key="id"):
    getter = itemgetter(key)
    a = sorted(first, key=getter)
    b = sorted(two, key=getter)
    msg = "\n"
    for x, y in zip_longest(a, b):
        msg = msg + f"{x}\n{y}\n\n"
    assert a == b, msg
    return True


def ss(fn, *args, **kwargs):
    """run inline dbsession"""
    with db_session:
        return fn(*args, **kwargs)


def check_super_init(parent, enfant, *args, fn="__init__", **kwargs):
    parent = ".".join((parent, fn))
    with patch(parent) as m:
        try:
            enfant(*args, **kwargs)
        except Exception:
            pass
        assert m.called
        del enfant
        return True


@contextmanager
def check_begin_end(obj, name):
    lot = ["begin", "end"]
    for x in lot:
        setattr(obj, x + name, MagicMock())
    yield
    for x in lot:
        try:
            assert getattr(obj, "begin" + name).called
        except AssertionError:
            print(x)
