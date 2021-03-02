import pytest
from PyQt5.QtGui import QColor
from tests.python.fixtures import disable_log

from mycartable.types.bridge import Bridge
from mycartable.types.stylable import Stylable
from pony.orm import db_session


class Styled(Stylable, Bridge):
    entity_name = "Annotation"


def test_init(fk, bridge):
    a = fk.f_annotation(td=True)
    s = Styled.get(a["id"], parent=bridge)
    assert s._data["style"] == a["style"]


def test_set_field_style(fk, qtbot, bridge):
    a = fk.f_annotation(td=True)
    s = Styled.get(a["id"], parent=bridge)
    with qtbot.waitSignal(s.bgColorChanged):
        s.bgColor = QColor("#123456")
    with db_session:
        assert fk.db.Annotation[a["id"]].style.bgColor == QColor("#123456")
    with qtbot.assertNotEmitted(s.bgColorChanged):
        s.bgColor = QColor("#123456")

    # turue if succsse
    assert s._set_field_style("bgColor", "#111111")
    with disable_log():
        assert not s._set_field_style("bgfzeColor", "#111111")


def test_set_field_style_bad_value(fk, qtbot, bridge):
    a = fk.f_annotation(td=True)
    s = Styled.get(a["id"], parent=bridge)
    s.bgColor = QColor("#123456")  # reset du test

    # bad value in db
    with qtbot.assertNotEmitted(s.bgColorChanged):
        with disable_log():
            s.bgColor = 3.4
    assert s.bgColor == QColor("#123456")
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
def test_properties(fk, qtbot, name, value, bridge):
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
    s = Styled.get(a["id"], parent=bridge)
    with qtbot.waitSignal(getattr(s, name + "Changed")):
        setattr(s, name, value)
    # pas d'"émission si pas de changement
    with qtbot.assertNotEmitted(getattr(s, name + "Changed")):
        setattr(s, name, value)
    with db_session:
        res = fk.db.Annotation[a["id"]].to_dict()
        assert res["style"][name] == value


#
