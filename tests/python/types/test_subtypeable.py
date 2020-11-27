from mycartable.types import Bridge
from mycartable.types import SubTypeAble


class Subtyped(SubTypeAble, Bridge):
    entity_name = "ble"


class MainSection(SubTypeAble, Bridge):
    entity_name = "Section"

    @staticmethod
    def available_subclass():
        return [MainSection, SubSection]


class SubSection(SubTypeAble, Bridge):
    entity_name = "TextSection"


def test_classtype(fk):
    s = Subtyped({"classtype": "bla"})
    assert s.classtype == "bla"


def test_new(fk):
    p = fk.f_page()
    # base class
    normal = MainSection.new(page=str(p.id))
    assert isinstance(normal, MainSection)
    # sublcass
    sub = MainSection.new(page=str(p.id), classtype="TextSection")
    assert isinstance(sub, SubSection)


def test_new(fk):
    p = fk.f_page()
    # base class
    normal = MainSection.new(page=str(p.id))
    assert isinstance(normal, MainSection)
    # sublcass
    sub = MainSection.new(page=str(p.id), classtype="TextSection")
    assert isinstance(sub, SubSection)


def test_get(fk):
    m = fk.f_section(td=True)
    s = fk.f_textSection(td=True)
    # base class
    normal = MainSection.get(m["id"])
    assert isinstance(normal, MainSection)
    normaldict = MainSection.get(m)
    assert isinstance(normal, MainSection)
    assert normal == normaldict
    # sublcass
    sub = MainSection.get(s["id"])
    assert isinstance(sub, SubSection)
    subdict = MainSection.get(s)
    assert isinstance(sub, SubSection)
    assert sub == subdict
