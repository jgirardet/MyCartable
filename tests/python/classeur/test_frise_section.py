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
    a.zones[2]["legendes"] = [fk.f_friseLegende(td=True, texte="bla")]
    assert a.data(a.index(1, 0), Qt.DisplayRole) == b._zones[1]["texte"]
    assert a.data(a.index(5, 0), Qt.DisplayRole) is None
    assert a.data(a.index(0, 0), Qt.BackgroundRole) == QColor("blue")
    assert a.data(a.index(2, 0), a.RatioRole) == 0.45
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

    assert a.data(a.index(1, 0), Qt.DisplayRole) == "blabla"
    assert a.data(a.index(5, 0), Qt.DisplayRole) is None
    assert a.data(a.index(0, 0), Qt.BackgroundRole) == QColor("purple")
    assert a.data(a.index(2, 0), a.RatioRole) == 0.99

    with db_session:
        assert ddbr.ZoneFrise[a.zones[1]["id"]].texte == "blabla"
        assert ddbr.ZoneFrise[a.zones[0]["id"]].style.bgColor == QColor("purple")
        assert ddbr.ZoneFrise[a.zones[2]["id"]].ratio == 0.99


def test_set_data_undo_redo(fm, ddbr):
    b = fm(3)
    a = b.model
    a.zones[0]["style"]["bgColor"] = QColor("blue")
    a.zones[2]["ratio"] = 0.45
    a.setData(a.index(0, 0), QColor("purple"), Qt.BackgroundRole)
    assert a.data(a.index(0, 0), Qt.BackgroundRole) == QColor("purple")
    with db_session:
        assert ddbr.ZoneFrise[a.zones[0]["id"]].style.bgColor == QColor("purple")

    b.undoStack.undo()
    assert a.data(a.index(0, 0), Qt.BackgroundRole) == QColor("blue")
    with db_session:
        assert ddbr.ZoneFrise[a.zones[0]["id"]].style.bgColor == QColor("blue")

    b.undoStack.redo()
    assert a.data(a.index(0, 0), Qt.BackgroundRole) == QColor("purple")
    with db_session:
        assert ddbr.ZoneFrise[a.zones[0]["id"]].style.bgColor == QColor("purple")


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


def test_append_and_add_row(fm, qtbot):
    b = fm(3)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeInserted, a.rowsInserted]):
        a.add()
    assert a.rowCount() == 4
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[1]["id"]
    assert a.zones[2]["id"] == b._zones[2]["id"]
    assert a.zones[3]["texte"] == "new"
    b.undoStack.undo()
    assert a.rowCount() == 3
    b.undoStack.redo()
    assert a.rowCount() == 4


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


def test_move_undo_redo(fm, qtbot):
    b = fm(5)
    a = b.model
    with qtbot.waitSignals([a.rowsAboutToBeMoved, a.rowsMoved]):
        assert a.move(1, 3)
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[2]["id"]
    assert a.zones[2]["id"] == b._zones[1]["id"]
    assert a.zones[3]["id"] == b._zones[3]["id"]
    assert a.zones[4]["id"] == b._zones[4]["id"]

    b.undoStack.undo()
    assert a.zones == b._zones
    b.undoStack.redo()
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[2]["id"]
    assert a.zones[2]["id"] == b._zones[1]["id"]
    assert a.zones[3]["id"] == b._zones[3]["id"]
    assert a.zones[4]["id"] == b._zones[4]["id"]

    # assert a.zones[0]["id"] == b._zones[0]["id"]
    # assert a.zones[1]["id"] == b._zones[1]["id"]
    # assert a.zones[2]["id"] == b._zones[2]["id"]
    # assert a.zones[3]["id"] == b._zones[3]["id"]
    # assert a.zones[4]["id"] == b._zones[4]["id"]


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
    backup = a.zones[4]
    with qtbot.waitSignals([a.rowsAboutToBeRemoved, a.rowsRemoved]):
        assert a.remove(4)
    assert a.rowCount(4)
    assert a.zones[0]["id"] == b._zones[0]["id"]
    assert a.zones[1]["id"] == b._zones[1]["id"]
    assert a.zones[2]["id"] == b._zones[2]["id"]
    assert a.zones[3]["id"] == b._zones[3]["id"]

    b.undoStack.undo()
    assert a.rowCount(5)
    assert a.zones[4] == backup

    b.undoStack.redo()
    assert a.rowCount(4)


def test_remove_legende(fm, fk, qtbot):
    b = fm(1)
    a = b.model
    a.zones[0]["legendes"] = [
        fk.f_friseLegende(td=True, texte="bla", zone=a.zones[0]["id"]),
        fk.f_friseLegende(td=True, texte="ble", zone=a.zones[0]["id"]),
        fk.f_friseLegende(td=True, texte="bli", zone=a.zones[0]["id"]),
    ]
    l = a.zones[0]["legendes"]
    with qtbot.waitSignal(a.legendeRemoved):
        a.removeLegende(0, 1)
    assert len(l) == 2
    with qtbot.waitSignal(a.legendeAdded):
        b.undoStack.undo()
    l = a.zones[0]["legendes"]
    assert len(l) == 3
    with qtbot.waitSignal(a.legendeRemoved):
        b.undoStack.redo()
    l = a.zones[0]["legendes"]
    assert len(l) == 2


def test_add_legende(fm, fk, qtbot):
    b = fm(1)
    a = b.model
    a.zones[0]["legendes"] = [
        fk.f_friseLegende(td=True, texte="bla", zone=a.zones[0]["id"]),
        fk.f_friseLegende(td=True, texte="ble", zone=a.zones[0]["id"]),
        fk.f_friseLegende(td=True, texte="bli", zone=a.zones[0]["id"]),
    ]
    l = a.zones[0]["legendes"]
    with qtbot.waitSignal(a.legendeAdded):
        a.addLegende(0, {"relativeX": 0.3, "side": True, "zone": a.zones[0]["id"]})
    assert len(l) == 4
    with qtbot.waitSignal(a.legendeRemoved):
        b.undoStack.undo()
    l = a.zones[0]["legendes"]
    assert len(l) == 3
    with qtbot.waitSignal(a.legendeAdded):
        b.undoStack.redo()
    l = a.zones[0]["legendes"]
    assert len(l) == 4


def test_update_legende(fm, fk, qtbot):
    b = fm(1)
    a = b.model
    a.zones[0]["legendes"] = [
        fk.f_friseLegende(td=True, texte="bla", zone=a.zones[0]["id"]),
    ]
    leg = a.zones[0]["legendes"][0]
    with qtbot.waitSignal(a.legendeUpdated):
        a.updateLegende(0, 0, {"texte": "bloum"})
    with db_session:
        assert fk.db.FriseLegende[leg["id"]].texte == "bloum"

    with qtbot.waitSignal(a.legendeUpdated):
        b.undoStack.undo()
    with db_session:
        assert fk.db.FriseLegende[leg["id"]].texte == "bla"

    with qtbot.waitSignal(a.legendeUpdated):
        b.undoStack.redo()
    with db_session:
        assert fk.db.FriseLegende[leg["id"]].texte == "bloum"
