import pytest
from mycartable.types import Bridge
from mycartable.types import SubTypeAble


class Subtyped(SubTypeAble, Bridge):
    entity_name = "ble"


class MainSection(SubTypeAble, Bridge):
    entity_name = "Section"

    @staticmethod
    def available_subclass():
        return [MainSection, SubSection]


class SubSection(MainSection):
    entity_name = "TextSection"


def test_classtype(fk, bridge):
    s = Subtyped({"classtype": "bla"}, parent=bridge)
    assert s.classtype == "bla"


def test_get_class(fk):
    assert MainSection.get_class({"classtype": "Section"}) == MainSection
    assert MainSection.get_class({}) == MainSection
    assert MainSection.get_class("Section") == MainSection
    assert MainSection.get_class({"classtype": "TextSection"}) == SubSection
    assert MainSection.get_class("TextSection") == SubSection


def test_available_not_implemented():
    with pytest.raises(NotImplementedError):
        Subtyped.get_class("aa")


def test_new_sub(fk, bridge):
    p = fk.f_page()
    text = MainSection.new_sub(classtype="TextSection", page=p.id, parent=bridge)
    assert isinstance(text, SubSection)
    text = MainSection.new_sub(classtype="Section", page=p.id, parent=bridge)
    assert isinstance(text, MainSection)
