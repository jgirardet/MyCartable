from copy import copy
from uuid import uuid4, UUID

import pytest
from mycartable.types.bridge import Bridge
from mycartable.types.dtb import DTB
from pony.orm import db_session
from loguru_caplog import loguru_caplog as caplog


@pytest.fixture()
def dummyClassPage():
    class Page(Bridge):
        entity_name = "Page"

    return Page


def test_init(fk, dummyClassPage):
    p = fk.f_page(td=True)
    b = dummyClassPage(data=p)
    assert b.entity_name == "Page"
    assert b.id == str(p["id"])
    assert isinstance(b.dtb, DTB)
    assert b.data == p


def test_set_property(fk, dummyClassPage):
    print(Bridge.entity_name)
    p = fk.f_page()
    b = dummyClassPage.get(p.id)
    b.titre = "NonNon"
    b._set_field("titre", "Blabla")
    with db_session:
        assert fk.db.Page[p.id].titre == "Blabla"


def test_new(fk, dummyClassPage):
    g = fk.f_activite()
    p = dummyClassPage.new(activite=str(g.id), titre="bla")
    assert p._data["titre"] == "bla"

    p = dummyClassPage.new(**{"activite": str(g.id), "titre": "polumb"})
    assert p._data["titre"] == "polumb"


def test_get_by_id(fk, dummyClassPage):
    p = fk.f_page(td=True)
    x = dummyClassPage.get(p["id"])
    assert x.data == p
    x = dummyClassPage.get(UUID(p["id"]))
    assert x.data == p


def test_get_by_dict(fk, dummyClassPage):
    p = fk.f_page(td=True)
    x = dummyClassPage.get(p)
    assert x.data == p


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
