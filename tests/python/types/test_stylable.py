import pytest
from PySide2.QtGui import QColor
from mycartable.classeur import Annotation
from mycartable.types.bridge import Bridge
from mycartable.types.stylable import Stylable
from pony.orm import db_session


class Styled(Stylable, Annotation):
    pass


def test_init(fk):
    a = fk.f_annotation(td=True)
    s = Styled.get(a["id"])
    assert s._data["style"] == a["style"]


def test_set_field_style(fk, qtbot):
    a = fk.f_annotation(td=True)
    s = Styled.get(a["id"])
    with qtbot.waitSignal(s.bgColorChanged):
        s.bgColor = QColor("#123456")
    with db_session:
        assert fk.db.Annotation[a["id"]].style.bgColor == QColor("#123456")


@pytest.mark.parametrize(
    "name, value",
    [
        ("bgColor", QColor("purple")),
        ("fgColor", QColor("purple")),
        ("underline", True),
        ("strikeout", True),
        ("pointSize", 2.0),
        ("weight", 2),
        ("family", "blim"),
    ],
)
def test_properties(fk, qtbot, name, value):
    a = fk.f_annotation(
        **{
            "x": 0.3,
            "y": 0.6,
            "style": {
                "" "bgColor": "red",
                "fgColor": "red",
                "underline": False,
                "pointSize": 5.0,
                "strikeout": False,
                "weight": 1,
                "family": "bla",
            },
        },
        td=True
    )
    s = Styled.get(a["id"])
    with qtbot.waitSignal(getattr(s, name + "Changed")):
        setattr(s, name, value)
    with db_session:
        res = fk.db.Annotation[a["id"]].to_dict()
        assert res["style"][name] == value


#
