from copy import copy
from uuid import uuid4, UUID

import pytest
from PySide2.QtCore import Property, Signal
from fixtures import disable_log
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


def test_new(fk, dummyClassPage):
    g = fk.f_activite()
    p = dummyClassPage.new(activite=str(g.id), titre="bla")
    assert p._data["titre"] == "bla"

    p = dummyClassPage.new(**{"activite": str(g.id), "titre": "polumb"})
    assert p._data["titre"] == "polumb"


def test_new_factory(fk):
    class DummySection(Bridge):
        entity_name = "Section"

    class TextDummy(DummySection):
        entity_name = "TextSection"

    g = fk.f_page()
    p = DummySection.new(
        page=str(g.id),
        text="aa",
        entity_factory="TextSection",
        class_factory=lambda x: TextDummy,
    )
    assert isinstance(p, TextDummy)

    p = DummySection.new(
        **{
            "page": str(g.id),
            "class_factory": lambda x: TextDummy,
            "entity_factory": "TextSection",
            "text": "blabla",
        }
    )
    assert isinstance(p, TextDummy)


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


def test_get_classtype(fk, dummyClassPage):
    class AlsoDummy(dummyClassPage):
        pass

    p = fk.f_page(td=True)

    # with dict
    x = dummyClassPage.get(p, class_factory=lambda x: AlsoDummy)
    assert x._data == p
    assert isinstance(x, AlsoDummy)

    # with int
    x = dummyClassPage.get(p["id"], class_factory=lambda x: AlsoDummy)
    assert x._data == p
    assert isinstance(x, AlsoDummy)


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
    y = dummyClassPage.get(x.id)
    assert x == y
