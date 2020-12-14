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
)

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
