import pytest
from mycartable.classeur import SectionFactory, ImageSection
from mycartable.classeur.sections import TextSection, Section

"""
Section
"""


def test_base_section(fk):
    a = fk.f_textSection(td=True)
    s = Section.get(a["id"])
    assert a == s._data
    assert s.classtype == "TextSection"


"""
Factory
"""


@pytest.mark.parametrize(
    "nom",
    [
        "textSection",
        "imageSection",
    ],
)
def test_get_section_donne_la_bonne(fk, nom):
    b = getattr(fk, "f_" + nom)(td=True)
    assert SectionFactory.get(b["id"]).classtype == nom[0].capitalize() + nom[1:]


@pytest.mark.parametrize(
    "nom, classtype,params",
    [
        ("TextSection", TextSection, {}),
        ("ImageSection", ImageSection, {"path": "sc1.png"}),
    ],
)
def test_new_section_donne_la_bonne(fk, nom, classtype, params, resources):
    page = fk.f_page()
    if "path" in params:
        params["path"] == str(resources / "sc1.png")
    # Non params
    new_sec = SectionFactory.new(page.id, nom, **params)
    assert isinstance(new_sec, classtype)
    assert new_sec.data["page"] == str(page.id)
    # with params
    new_sec = SectionFactory.new(
        page.id, nom, **{"id": "54830d99-220c-4a0a-ba18-47327bb729e1", **params}
    )
    assert isinstance(new_sec, classtype)
    assert new_sec.id == "54830d99-220c-4a0a-ba18-47327bb729e1"
