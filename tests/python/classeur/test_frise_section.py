import pytest
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QColor
from mycartable.classeur import FriseSection, Page
from mycartable.classeur.sections.frise import FriseModel
from pony.orm import db_session


@pytest.fixture()
def fm(fk, bridge):
    def wrapped(nb):

        x = fk.f_friseSection()
        _zones = fk.b_zoneFrise(nb, frise=x.id, td=True)
        p = Page.get(x.page.id, parent=bridge)
        f = p.get_section(0)
        f._zones = _zones
        return f

    return wrapped


def test_base(fk, bridge, qtbot):
    x = fk.f_friseSection(height=3, titre="aaa")
    p = Page.get(x.page.id, parent=bridge)
    a = p.get_section(0)
    assert a.id == str(x.id)
    assert a.height == 3
    assert a.titre == "aaa"
    with qtbot.waitSignals([a.heightChanged, a.titreChanged]):
        a.height = 5
        a.titre = "bbb"
    with db_session:
        it = fk.db.FriseSection[x.id]
        assert it.titre == "bbb"
        assert it.height == 5

    assert isinstance(a.model, FriseModel)


def test_base_undo_redo(fsec, sec_utils):
    props = {"height": 3, "titre": "aaa"}
    a = fsec("FriseSection", **props)
    sec_utils.test_set_property_undo_redo(a, **props)
    sec_utils.test_set_property_undo_redo(a, titre="cc")


def test_data(fm, fk):
    b = fm(3)
    a = b.model
    a.zones[0]["style"]["bgColor"] = QColor("blue")
    a.zones[2]["ratio"] = 0.45
    a.zones[1]["style"]["strikeout"] = True
    a.zones[2]["separatorText"] = "un époque"
    a.zones[2]["legendes"] = [fk.f_friseLegende(td=True, texte="bla")]
    assert a.data(a.index(1, 0), Qt.DisplayRole) == b._zones[1]["texte"]
    assert a.data(a.index(5, 0), Qt.DisplayRole) is None
    assert a.data(a.index(0, 0), Qt.BackgroundRole) == QColor("blue")
    assert a.data(a.index(2, 0), a.RatioRole) == 0.45
    assert a.data(a.index(2, 0), a.SeparatorPositionRole) is False
    assert a.data(a.index(1, 0), a.SeparatorPositionRole) is True
    assert a.data(a.index(2, 0), a.SeparatorTextRole) == "un époque"
    assert a.data(a.index(2, 0), a.LegendesRole)[0]["texte"] == "bla"
    assert a.data(a.index(2, 0), a.ZoneIdRole) == a.zones[2]["id"]


def test_set_data(fm, ddbr):
    b = fm(3)
    a = b.model
    a.zones[0]["style"]["bgColor"] = QColor("blue")
    a.zones[2]["ratio"] = 0.45
    a.setData(a.index(1, 0), "blabla", Qt.EditRole)
    a.setData(a.index(5, 0), "hehe", Qt.DisplayRole)
    a.setData(a.index(0, 0), QColor("purple"), Qt.BackgroundRole)
    a.setData(a.index(2, 0), 0.99, a.RatioRole)
    a.setData(a.index(2, 0), True, a.SeparatorPositionRole)
    a.setData(a.index(2, 0), "blabla", a.SeparatorTextRole)

    assert a.data(a.index(1, 0), Qt.DisplayRole) == "blabla"
    assert a.data(a.index(5, 0), Qt.DisplayRole) is None
    assert a.data(a.index(0, 0), Qt.BackgroundRole) == QColor("purple")
    assert a.data(a.index(2, 0), a.RatioRole) == 0.99
    assert a.data(a.index(2, 0), a.SeparatorPositionRole) is True
    assert a.data(a.index(2, 0), a.SeparatorTextRole) == "blabla"

    with db_session:
        assert ddbr.ZoneFrise[a.zones[1]["id"]].texte == "blabla"
        assert ddbr.ZoneFrise[a.zones[0]["id"]].style.bgColor == QColor("purple")
        assert ddbr.ZoneFrise[a.zones[2]["id"]].ratio == 0.99
        assert ddbr.ZoneFrise[a.zones[2]["id"]].style.strikeout is True
        assert ddbr.ZoneFrise[a.zones[2]["id"]].separatorText == "blabla"


def test_insert_rows(fm, qtbot):
    b = fm(3)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeInserted, a.rowsInserted]):
        a.insertRows(1, 2)
    assert a.rowCount() == 6
    assert a.zones[0] == b._zones[0]
    assert a.zones[1]["texte"] == "new"
    assert a.zones[2]["texte"] == "new"
    assert a.zones[3]["texte"] == "new"
    assert (
        a.zones[4]["id"] == b._zones[1]["id"]
    )  # on peut pas comparer tout à cause des positions
    assert a.zones[5]["id"] == b._zones[2]["id"]


def test_insert_rows_at_end(fm, qtbot):
    b = fm(3)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeInserted, a.rowsInserted]):
        a.insertRows(3, 1)
    assert a.rowCount() == 5
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[1]["id"]
    assert a.zones[2]["id"] == b._zones[2]["id"]
    assert a.zones[3]["texte"] == "new"
    assert a.zones[4]["texte"] == "new"


def test_insert_rows_at_start(fm, qtbot):
    b = fm(3)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeInserted, a.rowsInserted]):
        a.insertRows(0, 1)
    assert a.rowCount() == 5
    assert a.zones[0]["texte"] == "new"
    assert a.zones[1]["texte"] == "new"
    assert a.zones[2]["id"] == b._zones[0]["id"]
    assert (
        a.zones[3]["id"] == b._zones[1]["id"]
    )  # on peut pas comparer tout à cause des positions
    assert a.zones[4]["id"] == b._zones[2]["id"]


def test_insert_one_row(fm, qtbot):
    b = fm(3)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeInserted, a.rowsInserted]):
        a.insertRow(1)
    assert a.rowCount() == 4
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["texte"] == "new"
    assert a.zones[2]["id"] == b._zones[1]["id"]
    assert a.zones[3]["id"] == b._zones[2]["id"]


def test_append_row(fm, qtbot):
    b = fm(3)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeInserted, a.rowsInserted]):
        a.append()
    assert a.rowCount() == 4
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[1]["id"]
    assert a.zones[2]["id"] == b._zones[2]["id"]
    assert a.zones[3]["texte"] == "new"


def test_move_rows(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRows(QModelIndex(), 1, 1, QModelIndex(), 4)
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[3]["id"]
    assert a.zones[2]["id"] == b._zones[1]["id"]
    assert a.zones[3]["id"] == b._zones[2]["id"]
    assert a.zones[4]["id"] == b._zones[4]["id"]


def test_move_rows(fm, qtbot):
    b = fm(3)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRows(QModelIndex(), 0, 0, QModelIndex(), 2)
    assert a.zones[0]["id"] == b._zones[1]["id"]
    assert a.zones[1]["id"] == b._zones[0]["id"]
    assert a.zones[2]["id"] == b._zones[2]["id"]
    # assert a.zones[3]["id"] == b._zones[2]["id"]
    # assert a.zones[4]["id"] == b._zones[4]["id"]


def test_move_rows_ends(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRows(QModelIndex(), 2, 1, QModelIndex(), 5)
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[1]["id"]
    assert a.zones[2]["id"] == b._zones[4]["id"]
    assert a.zones[3]["id"] == b._zones[2]["id"]
    assert a.zones[4]["id"] == b._zones[3]["id"]


def test_move_rows_start(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRows(QModelIndex(), 2, 1, QModelIndex(), 0)
    assert a.zones[0]["id"] == b._zones[2]["id"]
    assert a.zones[1]["id"] == b._zones[3]["id"]
    assert a.zones[2]["id"] == b._zones[0]["id"]
    assert a.zones[3]["id"] == b._zones[1]["id"]
    assert a.zones[4]["id"] == b._zones[4]["id"]


def test_moveRow_down_top(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRow(3, 1)
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[3]["id"]
    assert a.zones[2]["id"] == b._zones[1]["id"]
    assert a.zones[3]["id"] == b._zones[2]["id"]
    assert a.zones[4]["id"] == b._zones[4]["id"]


def test_moveRow_top_down(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRow(1, 3)
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[2]["id"]
    assert a.zones[2]["id"] == b._zones[1]["id"]
    assert a.zones[3]["id"] == b._zones[3]["id"]
    assert a.zones[4]["id"] == b._zones[4]["id"]


def test_remove_rows_middle(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.removeRows(2, 1)
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[1]["id"]
    assert a.zones[2]["id"] == b._zones[4]["id"]


def test_remove_rows_end(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.removeRows(3, 1)
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[1]["id"]
    assert a.zones[2]["id"] == b._zones[2]["id"]


def test_remove_rows_end_depasse(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.removeRows(3, 3)
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[1]["id"]
    assert a.zones[2]["id"] == b._zones[2]["id"]


def test_remove_rows_debute(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.removeRows(0, 2)
    assert a.zones[0]["id"] == b._zones[3]["id"]
    assert a.zones[1]["id"] == b._zones[4]["id"]


def test_remove_row_debut(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.removeRows(0, 0)
    assert a.zones[0]["id"] == b._zones[1]["id"]
    assert a.zones[1]["id"] == b._zones[2]["id"]
    assert a.zones[2]["id"] == b._zones[3]["id"]
    assert a.zones[3]["id"] == b._zones[4]["id"]


def test_remove(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.remove(4)
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[1]["id"]
    assert a.zones[2]["id"] == b._zones[2]["id"]
    assert a.zones[3]["id"] == b._zones[3]["id"]


def test_remove(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.remove(0)
    assert a.zones[0]["id"] == b._zones[1]["id"]
    assert a.zones[1]["id"] == b._zones[2]["id"]
    assert a.zones[2]["id"] == b._zones[3]["id"]
    assert a.zones[3]["id"] == b._zones[4]["id"]
