import pytest
from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtGui import QColor
from package.page.frise_model import FriseModel
from pony.orm import db_session


@pytest.fixture()
def fm(fk, dao):
    def wrapped(nb):
        f = FriseModel()
        f._frise = fk.f_friseSection()
        f._zones = fk.b_zoneFrise(nb, frise=f._frise, td=True)
        f.dao = dao
        f.sectionId = f._frise.id
        return f

    return wrapped


def test_base(fk):
    # reset is called on sectionIf in the fixture
    a = FriseModel()
    assert a.zones == []
    assert a.sectionId == ""
    assert a._sectionItem == {}
    assert a.rowCount() == 0
    assert a.titre == ""


def test_init(fk, qtbot, dao):
    a = FriseModel()
    with qtbot.waitSignal(a.daoChanged):
        a.dao = dao

    # setup
    fr = fk.f_friseSection(titre="azerty", height=200)
    zz = fk.b_zoneFrise(2, frise=fr, td=True)
    with qtbot.waitSignals(
        [a.sectionIdChanged, a.modelReset, a.titreChanged, a.heightChanged]
    ):
        a.sectionId = str(fr.id)

        # after reset
    assert a.titre == "azerty"
    assert a.height == 200
    assert a.rowCount() == 2
    assert a.zones == zz


def test_data(fm, fk):
    a = fm(3)
    a.zones[0]["style"]["bgColor"] = "blue"
    a.zones[2]["ratio"] = 0.45
    a.zones[1]["style"]["strikeout"] = True
    a.zones[2]["separatorText"] = "un époque"
    a.zones[2]["legendes"] = [fk.f_friseLegende(td=True, texte="bla")]
    assert a.data(a.index(1, 0), Qt.DisplayRole) == a._zones[1]["texte"]
    assert a.data(a.index(5, 0), Qt.DisplayRole) is None
    assert a.data(a.index(0, 0), Qt.BackgroundRole) == QColor("blue")
    assert a.data(a.index(2, 0), a.RatioRole) == 0.45
    assert a.data(a.index(2, 0), a.SeparatorPositionRole) is False
    assert a.data(a.index(1, 0), a.SeparatorPositionRole) is True
    assert a.data(a.index(2, 0), a.SeparatorTextRole) == "un époque"
    assert a.data(a.index(2, 0), a.LegendesRole)[0]["texte"] == "bla"
    assert a.data(a.index(2, 0), a.ZoneIdRole) == a.zones[2]["id"]


def test_set_data(fm, ddbr):
    a = fm(3)
    a.zones[0]["style"]["bgColor"] = "blue"
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
    a = fm(3)
    with qtbot.waitSignals([a.rowsAboutToBeInserted, a.rowsInserted]):
        a.insertRows(1, 2)
    assert a.rowCount() == 6
    assert a.zones[0] == a._zones[0]
    assert a.zones[1]["texte"] == "new"
    assert a.zones[2]["texte"] == "new"
    assert a.zones[3]["texte"] == "new"
    assert (
        a.zones[4]["id"] == a._zones[1]["id"]
    )  # on peut pas comparer tout à cause des positions
    assert a.zones[5]["id"] == a._zones[2]["id"]


def test_insert_rows_at_end(fm, qtbot):
    a = fm(3)
    with qtbot.waitSignals([a.rowsAboutToBeInserted, a.rowsInserted]):
        a.insertRows(3, 1)
    assert a.rowCount() == 5
    assert a.zones[0]["id"] == a._zones[0]["id"]
    assert a.zones[1]["id"] == a._zones[1]["id"]
    assert a.zones[2]["id"] == a._zones[2]["id"]
    assert a.zones[3]["texte"] == "new"
    assert a.zones[4]["texte"] == "new"


def test_insert_rows_at_start(fm, qtbot):
    a = fm(3)
    with qtbot.waitSignals([a.rowsAboutToBeInserted, a.rowsInserted]):
        a.insertRows(0, 1)
    assert a.rowCount() == 5
    assert a.zones[0]["texte"] == "new"
    assert a.zones[1]["texte"] == "new"
    assert a.zones[2]["id"] == a._zones[0]["id"]
    assert (
        a.zones[3]["id"] == a._zones[1]["id"]
    )  # on peut pas comparer tout à cause des positions
    assert a.zones[4]["id"] == a._zones[2]["id"]


def test_insert_one_row(fm, qtbot):
    a = fm(3)
    with qtbot.waitSignals([a.rowsAboutToBeInserted, a.rowsInserted]):
        a.insertRow(1)
    assert a.rowCount() == 4
    assert a.zones[0]["id"] == a._zones[0]["id"]
    assert a.zones[1]["texte"] == "new"
    assert a.zones[2]["id"] == a._zones[1]["id"]
    assert a.zones[3]["id"] == a._zones[2]["id"]


def test_append_row(fm, qtbot):
    a = fm(3)
    with qtbot.waitSignals([a.rowsAboutToBeInserted, a.rowsInserted]):
        a.append()
    assert a.rowCount() == 4
    assert a.zones[0]["id"] == a._zones[0]["id"]
    assert a.zones[1]["id"] == a._zones[1]["id"]
    assert a.zones[2]["id"] == a._zones[2]["id"]
    assert a.zones[3]["texte"] == "new"


def test_move_rows(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRows(QModelIndex(), 1, 1, QModelIndex(), 4)
    assert a.zones[0]["id"] == a._zones[0]["id"]
    assert a.zones[1]["id"] == a._zones[3]["id"]
    assert a.zones[2]["id"] == a._zones[1]["id"]
    assert a.zones[3]["id"] == a._zones[2]["id"]
    assert a.zones[4]["id"] == a._zones[4]["id"]


def test_move_rows(fm, qtbot):
    a = fm(3)
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRows(QModelIndex(), 0, 0, QModelIndex(), 2)
    assert a.zones[0]["id"] == a._zones[1]["id"]
    assert a.zones[1]["id"] == a._zones[0]["id"]
    assert a.zones[2]["id"] == a._zones[2]["id"]
    # assert a.zones[3]["id"] == a._zones[2]["id"]
    # assert a.zones[4]["id"] == a._zones[4]["id"]


def test_move_rows_ends(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRows(QModelIndex(), 2, 1, QModelIndex(), 5)
    assert a.zones[0]["id"] == a._zones[0]["id"]
    assert a.zones[1]["id"] == a._zones[1]["id"]
    assert a.zones[2]["id"] == a._zones[4]["id"]
    assert a.zones[3]["id"] == a._zones[2]["id"]
    assert a.zones[4]["id"] == a._zones[3]["id"]


def test_move_rows_start(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRows(QModelIndex(), 2, 1, QModelIndex(), 0)
    assert a.zones[0]["id"] == a._zones[2]["id"]
    assert a.zones[1]["id"] == a._zones[3]["id"]
    assert a.zones[2]["id"] == a._zones[0]["id"]
    assert a.zones[3]["id"] == a._zones[1]["id"]
    assert a.zones[4]["id"] == a._zones[4]["id"]


def test_moveRow_down_top(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRow(3, 1)
    assert a.zones[0]["id"] == a._zones[0]["id"]
    assert a.zones[1]["id"] == a._zones[3]["id"]
    assert a.zones[2]["id"] == a._zones[1]["id"]
    assert a.zones[3]["id"] == a._zones[2]["id"]
    assert a.zones[4]["id"] == a._zones[4]["id"]


def test_moveRow_top_down(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.moveRow(1, 3)
    assert a.zones[0]["id"] == a._zones[0]["id"]
    assert a.zones[1]["id"] == a._zones[2]["id"]
    assert a.zones[2]["id"] == a._zones[1]["id"]
    assert a.zones[3]["id"] == a._zones[3]["id"]
    assert a.zones[4]["id"] == a._zones[4]["id"]


def test_remove_rows_middle(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.removeRows(2, 1)
    assert a.zones[0]["id"] == a._zones[0]["id"]
    assert a.zones[1]["id"] == a._zones[1]["id"]
    assert a.zones[2]["id"] == a._zones[4]["id"]


def test_remove_rows_end(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.removeRows(3, 1)
    assert a.zones[0]["id"] == a._zones[0]["id"]
    assert a.zones[1]["id"] == a._zones[1]["id"]
    assert a.zones[2]["id"] == a._zones[2]["id"]


def test_remove_rows_end_depasse(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.removeRows(3, 3)
    assert a.zones[0]["id"] == a._zones[0]["id"]
    assert a.zones[1]["id"] == a._zones[1]["id"]
    assert a.zones[2]["id"] == a._zones[2]["id"]


def test_remove_rows_debute(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.removeRows(0, 2)
    assert a.zones[0]["id"] == a._zones[3]["id"]
    assert a.zones[1]["id"] == a._zones[4]["id"]


def test_remove_row_debut(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.removeRows(0, 0)
    assert a.zones[0]["id"] == a._zones[1]["id"]
    assert a.zones[1]["id"] == a._zones[2]["id"]
    assert a.zones[2]["id"] == a._zones[3]["id"]
    assert a.zones[3]["id"] == a._zones[4]["id"]


def test_remove(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.remove(4)
    assert a.zones[0]["id"] == a._zones[0]["id"]
    assert a.zones[1]["id"] == a._zones[1]["id"]
    assert a.zones[2]["id"] == a._zones[2]["id"]
    assert a.zones[3]["id"] == a._zones[3]["id"]


def test_remove(fm, qtbot):
    a = fm(5)
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.remove(0)
    assert a.zones[0]["id"] == a._zones[1]["id"]
    assert a.zones[1]["id"] == a._zones[2]["id"]
    assert a.zones[2]["id"] == a._zones[3]["id"]
    assert a.zones[3]["id"] == a._zones[4]["id"]
