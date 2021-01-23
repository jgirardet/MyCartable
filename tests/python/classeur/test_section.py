import pytest
from mycartable.classeur import (
    ImageSection,
    OperationSection,
    AdditionSection,
    SoustractionSection,
    MultiplicationSection,
    DivisionSection,
    Section,
    TextSection,
    EquationSection,
    TableauSection,
    FriseSection,
    Page,
)
from pony.orm import db_session

"""
Section
"""

sub_classes = (
    Section,
    TextSection,
    ImageSection,
    EquationSection,
    OperationSection,
    AdditionSection,
    SoustractionSection,
    MultiplicationSection,
    DivisionSection,
    TableauSection,
    FriseSection,
)


def test_available_subclasses():
    assert Section.available_subclass() == sub_classes


@pytest.mark.parametrize(
    "_class",
    sub_classes,
)
def test_get_class(fk, _class):
    f_name = "f_" + _class.entity_name[0].lower() + _class.entity_name[1:]
    a = getattr(fk, f_name)(td=True)
    s = Section.get(a["id"])
    assert a == s._data
    assert s.classtype == _class.entity_name
    assert isinstance(s, _class)


@pytest.mark.parametrize(
    "_class",
    sub_classes,
)
def test_backup(fk, _class):
    f_name = "f_" + _class.entity_name[0].lower() + _class.entity_name[1:]
    a = getattr(fk, f_name)()
    s = Section.get(a.id)

    with db_session:
        assert a.backup() == getattr(fk.db, _class.entity_name)[a.id].backup()


def test_properties(fk):
    it = fk.f_section(td=True)
    p = Page.get(it["page"])
    sec = Section.get(it["id"], parent=p)
    assert sec.page == p
