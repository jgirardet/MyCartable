from copy import copy
from uuid import uuid4, UUID

import pytest
from PySide2.QtCore import Property, Signal, QObject
from tests.python.fixtures import disable_log, uuu
from mycartable.types.bridge import Bridge
from mycartable.types.dtb import DTB
from pony.orm import db_session
from loguru_caplog import loguru_caplog as caplog


@pytest.fixture()
def dummyClassPage():
    class Page(Bridge):
        entity_name = "Page"

        titreChanged = Signal()

        @Property(str, notify=titreChanged)
        def titre(self):
            return self._data["titre"]

        @titre.setter
        def titre_set(self, value: str):
            self.set_field("titre", value)

        lastPositionChanged = Signal()

        @Property(int, notify=lastPositionChanged)
        def lastPosition(self):
            return self._data["lastPosition"]

        @lastPosition.setter
        def lastPosition_set(self, value: int):
            self._set_field("lastPosition", value)
            self.lastPositionChanged.emit()

    return Page


def test_init(fk, dummyClassPage):
    p = fk.f_page(td=True)
    b = dummyClassPage(data=p)
    assert b.entity_name == "Page"
    assert b.id == str(p["id"])
    assert isinstance(b._dtb, DTB)
    assert b._data == p


def test_set_property(fk, dummyClassPage):
    p = fk.f_page()
    b = dummyClassPage.get(p.id)
    b.titre = "NonNon"
    assert b._set_field("titre", "Blabla")
    with disable_log():
        assert not b._set_field("titrfzee", "Blabla")
    with db_session:
        assert fk.db.Page[p.id].titre == "Blabla"


def test_set_field(fk, dummyClassPage, qtbot):
    a = dummyClassPage.get(fk.f_page(titre="bla", td=True))
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


def test_set(fk, qtbot, dummyClassPage):
    f = fk.f_page(titre="bla", lastPosition=3)
    p = dummyClassPage.get(f.id)
    with qtbot.waitSignals([p.titreChanged, p.lastPositionChanged]):
        p.set({"titre": "hello", "lastPosition": 99})
    with db_session:
        pa = fk.db.Page[p.id]
        assert pa.lastPosition == 99
        assert pa.titre == "hello"


def test_new(fk, dummyClassPage):
    g = fk.f_activite()
    p = dummyClassPage.new(activite=str(g.id), titre="bla")
    assert p._data["titre"] == "bla"

    p = dummyClassPage.new(**{"activite": str(g.id), "titre": "polumb"})
    assert p._data["titre"] == "polumb"

    # none
    class AAA(Bridge):
        entity_name = "a"

    assert AAA.new() is None


def test_get_by_id(fk, dummyClassPage):
    p = fk.f_page(td=True)
    x = dummyClassPage.get(p["id"])
    assert x._data == p
    x = dummyClassPage.get(UUID(p["id"]))
    assert x._data == p


def test_get_by_dict(fk, dummyClassPage):
    p = fk.f_page(td=True)
    x = dummyClassPage.get(p)
    assert x._data == p


def test_get_wrong_type(fk, dummyClassPage):
    assert dummyClassPage.get([]) is None


def test_get_with_parent(fk, dummyClassPage):
    a = QObject()
    p = fk.f_page(td=True)
    x = dummyClassPage.get(p["id"], parent=a)
    assert x._data == p
    assert x.parent() == a


def test_delete(fk, dummyClassPage):
    p = fk.f_page()
    dummyClassPage.get(str(p.id)).delete()
    with db_session:
        assert not fk.db.Page.exists(id=p.id)


def test_init_subclass():
    with pytest.raises(NotImplementedError):

        class Bla(Bridge):
            pass


def test_eq(dummyClassPage, fk):
    ac = fk.f_activite()
    x = dummyClassPage.new(activite=ac.id)
    z = dummyClassPage.new(activite=ac.id)
    y = dummyClassPage.get(x.id)
    assert x == y
    assert x != z
    assert x != 1


def test_get_class_with_new_and_get(fk):
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
    b = Bla.new(**{"page": p.id})
    c = Rex.new(**{"page": p.id})
    assert isinstance(b, Bla)
    assert isinstance(c, Child)
    # get
    assert isinstance(Bla.get(b.id), Bla)
    assert isinstance(Rex.get(c.id), Child)
