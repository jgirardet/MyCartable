import pytest
from mycartable.classeur import ImageSection
from mycartable.classeur.sections import TextSection, Section

"""
Section
"""


def test_base_section(fk):
    a = fk.f_textSection(td=True)
    s = Section.get(a["id"])
    assert a == s._data
    assert s.classtype == "TextSection"
