from itertools import zip_longest
from operator import itemgetter

from pony.orm import db_session


def compare(first, two, key='id'):
    getter = itemgetter(key)
    a = sorted(first, key=getter)
    b = sorted(two, key=getter)
    msg = "\n"
    for x,y in zip_longest(a,b):
        msg = msg+f"{x}\n{y}\n\n"
    assert a ==b, msg
    return True


def ss(fn, *args, **kwargs):
    """run inline dbsession"""
    with db_session:
        return fn(*args, **kwargs)