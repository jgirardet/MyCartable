import time
from itertools import zip_longest
from operator import itemgetter, attrgetter
from unittest.mock import patch, MagicMock

from pony.orm import db_session
from contextlib import contextmanager

from PySide2.QtGui import QFontInfo, QColor


def compare_items(first, two, key="id"):
    for x, y in zip(first, two):
        assert getattr(x, key) == getattr(y, key)


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
        assert getattr(obj, x + name).called, f"{x+name} not called"


EQUIVALENTS = {
    str: "QString",
    int: "int",
    dict: "QVariantMap",
    list: "QVariantList",
    None: "void",
    bool: "bool",
    QColor: "QColor",
    float: "double",
}


def check_args(fn, exp_args=[], exp_return_type=None, slot_order=0):

    if not isinstance(exp_args, (tuple, list)):
        exp_args = [exp_args] if exp_args is not None else None

    name = fn.__name__
    return_type, reste = fn._slots[slot_order].split()
    reste = reste.replace(name, "").replace("(", "").replace(")", "")
    args = reste.split(",")
    if args == [""]:
        args = []

    if exp_args:
        converted_args = [EQUIVALENTS[x] for x in exp_args]
    else:
        converted_args = []
    converted_return_type = EQUIVALENTS[exp_return_type]
    assert (
        return_type == converted_return_type
    ), f"{return_type} différent de {converted_return_type}"
    assert args == converted_args, f"{args} différent de {converted_args}"


def check_is_range(obj, fn, res):
    res = set(res)
    for i in res:
        assert getattr(obj, fn)(i), f" {i} should return True"
    non_compris = set(range(0, obj.size))
    non_compris = non_compris - res
    for i in non_compris:
        assert not getattr(obj, fn)(i), f" {i} should return False"


#
#
# def is_blockFormat(item):
#     block_style = item["style"]
#     level = item.name[-1]
#     char_style = item.span["style"]
#     format = getattr(blockformat, f"BF_H{level}")
#     template = f' margin-top:{format["topMargin"]}px; margin-bottom:{format["bottomMargin"]}px; margin-left:{format["leftMargin"]}px; margin-right:{format["rightMargin"]}px; -qt-block-indent:{format["indent"]}; text-indent:0px;'
#
#     return block_style == template


def wait():
    time.sleep(1 / 1000)


def compare_block_format(lhs, rhs):
    attrs = [
        "alignment",
        "bottomMargin",
        "headingLevel",
        "indent",
        "leftMargin",
        "lineHeight",
        "lineHeightType",
        "marker",
        "nonBreakableLines",
        "pageBreakPolicy",
        "rightMargin",
    ]

    for attr in attrs:
        assert getattr(lhs, attr) == getattr(rhs, attr)
    return True


def compare_char_format(lhs, rhs, exclude=[]):
    """bizarement un charformat psa toujours égal même si toutes propriété égale"""
    try:
        assert lhs == rhs
    except AssertionError:
        pass
    else:
        return True

    # si comparaison de base échoue, on fait le détail

    attrs = [
        "anchorHref",
        "anchorName",
        "anchorNames",
        "font",
        "fontCapitalization",
        "fontFamilies",
        "fontFamily",
        "fontFixedPitch",
        "fontHintingPreference",
        "fontItalic",
        "fontKerning",
        "fontLetterSpacing",
        "fontLetterSpacingType",
        "fontOverline",
        "fontPointSize",
        "fontStretch",
        "fontStrikeOut",
        "fontStyleHint",
        "fontStyleName",
        "fontStyleStrategy",
        "fontUnderline",
        "fontWeight",
        "tableCellColumnSpan",
        "tableCellRowSpan",
        "textOutline",
        "toolTip",
        "underlineColor",
        "underlineStyle",
        "verticalAlignment",
    ]

    for attr in attrs:
        if attr in exclude:
            continue
        r = getattr(lhs, attr)()
        l = getattr(rhs, attr)()
        assert r == l, f"{attr}: {r}!={l}"
    return True
