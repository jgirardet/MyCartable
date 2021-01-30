from uuid import UUID

import pytest
from PyQt5.QtCore import pyqtProperty, pyqtSignal, QObject
from PyQt5.QtWidgets import QUndoStack
from tests.python.fixtures import disable_log
from mycartable.types.bridge import Bridge
from mycartable.types.dtb import DTB
from pony.orm import db_session


@pytest.fixture()
def dummyClassPage():
    class Page(Bridge):
        entity_name = "Page"

        titreChanged = pyqtSignal()

        @pyqtProperty(str, notify=titreChanged)
        def titre(self):
            return self._data["titre"]

        @titre.setter
        def titre(self, value: str):
            self.set_field("titre", value)

        lastPositionChanged = pyqtSignal()

        @pyqtProperty(int, notify=lastPositionChanged)
        def lastPosition(self):
            return self._data["lastPosition"]

        @lastPosition.setter
        def lastPosition(self, value: int):
            self.set_field("lastPosition", value)
            self.lastPositionChanged.emit()

    return Page


def test_init(fk, dummyClassPage, bridge):
    p = fk.f_page(td=True)
    b = dummyClassPage(data=p, parent=bridge)
    assert b.entity_name == "Page"
    assert b.id == str(p["id"])
    assert isinstance(b._dtb, DTB)
    assert b._data == p


def test_set_property(fk, dummyClassPage, bridge):
    p = fk.f_page()
    b = dummyClassPage.get(p.id, parent=bridge)
    b.titre = "NonNon"
    assert b._set_field("titre", "Blabla")
    with disable_log():
        assert not b._set_field("titrfzee", "Blabla")
    with db_session:
        assert fk.db.Page[p.id].titre == "Blabla"


def test_set_field(fk, dummyClassPage, qtbot, bridge):
    a = dummyClassPage.get(fk.f_page(titre="bla", td=True), parent=bridge)
    with qtbot.waitSignal(a.titreChanged):
        a.titre = "eee"

    with qtbot.assertNotEmitted(a.titreChanged):
        a.titre = "eee"
    with qtbot.waitSignal(a.titreChanged):
        a.titre = "iii"
    with db_session:
        assert fk.db.Page[a.id].titre == "iii"

    # fail in db
    with qtbot.assertNotEmitted(a.titreChanged):
        with disable_log():
            a.titre = []  # datatype
    assert a.titre == "iii"
    with db_session:
        assert fk.db.Page[a.id].titre == "iii"


def test_set(fk, qtbot, dummyClassPage, bridge):
    f = fk.f_page(titre="bla", lastPosition=3)
    p = dummyClassPage.get(f.id, parent=bridge)
    with qtbot.waitSignals([p.titreChanged, p.lastPositionChanged]):
        p.set({"titre": "hello", "lastPosition": 99})
    with db_session:
        pa = fk.db.Page[p.id]
        assert pa.lastPosition == 99
        assert pa.titre == "hello"
    #
    with qtbot.waitSignals([p.titreChanged, p.lastPositionChanged]):
        p.undoStack.undo()
    with db_session:
        pa = fk.db.Page[p.id]
        assert pa.lastPosition == 3
        assert pa.titre == "bla"
    print(p.undoStack.count())
    with qtbot.waitSignals([p.titreChanged, p.lastPositionChanged]):
        p.undoStack.redo()
    with db_session:
        pa = fk.db.Page[p.id]
        assert pa.lastPosition == 99
        assert pa.titre == "hello"


def test_new(fk, dummyClassPage, bridge):
    g = fk.f_activite()
    p = dummyClassPage.new(activite=str(g.id), titre="bla", parent=bridge)
    assert p._data["titre"] == "bla"

    p = dummyClassPage.new(**{"activite": str(g.id), "titre": "polumb"}, parent=bridge)
    assert p._data["titre"] == "polumb"

    # none
    class AAA(Bridge):
        entity_name = "a"

    assert AAA.new(parent=bridge) is None


def test_get_by_id(fk, dummyClassPage, bridge):
    p = fk.f_page(td=True)
    x = dummyClassPage.get(p["id"], parent=bridge)
    assert x._data == p
    x = dummyClassPage.get(UUID(p["id"]), parent=bridge)
    assert x._data == p


def test_get_by_dict(fk, dummyClassPage, bridge):
    p = fk.f_page(td=True)
    x = dummyClassPage.get(p, parent=bridge)
    assert x._data == p


def test_get_wrong_type(fk, dummyClassPage, bridge):
    assert dummyClassPage.get([], parent=bridge) is None


def test_get_with_parent(fk, dummyClassPage, bridge):
    p = fk.f_page(td=True)
    x = dummyClassPage.get(p["id"], parent=bridge)
    assert x._data == p
    assert x.parent() == bridge


def test_delete(fk, dummyClassPage, bridge):
    p = fk.f_page()
    dummyClassPage.get(str(p.id), parent=bridge).delete()
    with db_session:
        assert not fk.db.Page.exists(id=p.id)


def test_init_subclass():
    with pytest.raises(NotImplementedError):

        class Bla(Bridge):
            pass


def test_eq(dummyClassPage, fk, bridge):
    ac = fk.f_activite()
    x = dummyClassPage.new(activite=ac.id, parent=bridge)
    z = dummyClassPage.new(activite=ac.id, parent=bridge)
    y = dummyClassPage.get(x.id, parent=bridge)
    assert x == y
    assert x != z
    assert x != 1


def test_get_class_with_new_and_get(fk, bridge):
    class Child(Bridge):
        entity_name = "Section"

    class Rex(Bridge):
        entity_name = "Section"

        def get_class(self):
            return Child

    class Bla(Bridge):
        entity_name = "Section"

    p = fk.f_page()
    # new
    b = Bla.new(**{"page": p.id}, parent=bridge)
    c = Rex.new(**{"page": p.id}, parent=bridge)
    assert isinstance(b, Bla)
    assert isinstance(c, Child)
    # get
    assert isinstance(Bla.get(b.id, parent=bridge), Bla)
    assert isinstance(Rex.get(c.id, parent=bridge), Child)
