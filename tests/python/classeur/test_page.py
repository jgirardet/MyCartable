from unittest.mock import patch, call

import pytest
from PySide2.QtCore import QModelIndex, Qt
from pytestqml.qt import QObject
from tests.python.fixtures import ss, check_args, disable_log
from mycartable.classeur import (
    Page,
    PageModel,
    TextSection,
    Section,
    ImageSection,
    EquationSection,
    OperationSection,
    AdditionSection,
    SoustractionSection,
    MultiplicationSection,
    DivisionSection,
    TableauSection,
    FriseSection,
    Converter,
)
from mycartable.package.utils import shift_list
from pony.orm import db_session, make_proxy


def test_subclassing(fk):
    ac = fk.f_activite()
    x = Page.new(activite=ac.id)
    y = Page.get(x.id)
    assert x == y
    assert x.delete()
    with disable_log():
        assert Page.get(y.id) is None


def test_properties(fk):
    ac = fk.f_activite()
    p = Page.new(titre="bla", activite=ac.id, lastPosition=5)

    # titre
    p.titre = "Haha"
    assert p.titre == "Haha"
    assert ss(lambda: fk.db.Page[p.id].titre) == "Haha"

    # lastused
    assert p.lastPosition == 5
    p.lastPosition = 2
    assert p.lastPosition == 2

    # matiere
    assert p.matiereId == str(ac.matiere.id)

    # classert
    a = QObject()
    p.setParent(a)
    assert p.classeur == a


def test_property_model(fk):
    ac = fk.f_activite()
    p = Page.new(activite=ac.id)
    assert isinstance(p.model, PageModel)
    assert p.model.parent() == p


def test_base_init(fk):
    pg = fk.f_page(td=True)
    p = Page.get(pg["id"])
    assert p.model._data == pg
    assert p.model.rowCount(QModelIndex()) == 0
    assert p.matiereId == p.matiere.id == pg["matiere"]


@pytest.mark.parametrize(
    "nom, sectionclass",
    [
        ("textSection", TextSection),
        ("section", Section),
        ("imageSection", ImageSection),
        ("equationSection", EquationSection),
        ("operationSection", OperationSection),
        ("additionSection", AdditionSection),
        ("soustractionSection", SoustractionSection),
        ("multiplicationSection", MultiplicationSection),
        ("divisionSection", DivisionSection),
        ("tableauSection", TableauSection),
        ("friseSection", FriseSection),
    ],
)
def test_data_role(fk, nom, sectionclass):
    sec = getattr(fk, "f_" + nom)(td=True)
    p = Page.get(sec["page"])
    a = p.model
    res = a.data(a.index(0, 0), a.SectionRole)
    assert isinstance(res, sectionclass)
    assert res.id == sec["id"]
    assert res.classtype == sec["classtype"]
    # invalid index
    assert a.data(a.index(99, 99), a.SectionRole) is None
    # no good role
    assert a.data(a.index(0, 0), 99999) is None


def test_rowCount(fk):
    pg = fk.f_page()
    fk.b_section(3, page=pg.id)
    p = Page.get(str(pg.id))
    a = p.model
    assert a.rowCount(QModelIndex()) == 3
    assert a.count == 3


def test_roleNames(fk):
    pg = fk.f_page()
    p = Page.get(str(pg.id))
    a = p.model
    assert PageModel.SectionRole in a.roleNames()


@pytest.mark.parametrize(
    "source, target, lastposition",
    [
        (0, 0, 9),
        (0, 1, 9),
        (0, 2, 1),
        (0, 3, 2),
        (0, 4, 9),
        (1, 0, 0),
        (1, 1, 9),
        (1, 2, 9),
        (1, 3, 2),
        (1, 4, 9),
        (2, 0, 0),
        (2, 1, 1),
        (2, 2, 9),
        (2, 3, 9),
        (2, 4, 9),
        (3, 0, 9),
        (3, 1, 9),
        (3, 2, 9),
        (3, 3, 9),
        (3, 4, 9),
        (4, 0, 9),
        (4, 1, 9),
        (4, 2, 9),
        (4, 3, 9),
        (4, 4, 9),
    ],
)
def test_move(fk, source, target, lastposition):
    pg = fk.f_page(lastPosition=9)
    secs_ids_pre = [str(x.id) for x in fk.b_section(3, page=pg.id)]
    p = Page.get(str(pg.id))
    a = p.model
    new_order = shift_list(secs_ids_pre, source, 1, target)
    res = a.move(source, target)
    with db_session:
        new_secs_dict = [
            s.to_dict()
            for s in fk.db.Page[pg.id].sections.order_by(lambda x: x.position)
        ]
        new_secs_ids = [s["id"] for s in new_secs_dict]
        assert a._data["sections"] == new_secs_ids
    if res:
        assert new_secs_ids != secs_ids_pre
        assert new_secs_ids == new_order
    else:
        assert new_secs_ids == secs_ids_pre
    assert [s["position"] for s in new_secs_dict] == [0, 1, 2]
    assert a.page.lastPosition == lastposition


@pytest.mark.parametrize(
    "idx, res, lastpos",
    [
        (
            0,
            [
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ],
            0,
        ),
        (
            1,
            [
                "00000000-0000-0000-0000-000000000000",
                "22222222-2222-2222-2222-222222222222",
            ],
            1,
        ),
        (
            2,
            [
                "00000000-0000-0000-0000-000000000000",
                "11111111-1111-1111-1111-111111111111",
            ],
            1,
        ),
        (
            3,
            [
                "00000000-0000-0000-0000-000000000000",
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ],
            2,
        ),
    ],
)
def test_removeRows(fk, idx, res, lastpos):
    pg = fk.f_page(lastPosition=0)
    ids = [
        "00000000-0000-0000-0000-000000000000",
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
    ]
    [fk.f_section(id=x, page=pg.id) for x in ids]
    p = Page.get(str(pg.id))
    a = p.model
    assert a.remove(idx)
    assert a._data["sections"] == res
    with db_session:
        new_secs_dict = [
            s.to_dict()
            for s in fk.db.Page[pg.id].sections.order_by(lambda x: x.position)
        ]
    new_secs_ids = [s["id"] for s in new_secs_dict]
    assert a._data["sections"] == new_secs_ids
    assert a.page.lastPosition == lastpos


@pytest.mark.parametrize(
    "args, kwargs, res, lastpos",
    [
        (
            ["TextSection", 0],
            {},
            [
                "33333333-3333-3333-3333-333333333333",
                "00000000-0000-0000-0000-000000000000",
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ],
            0,
        ),
        (
            ["TextSection", 1],
            {},
            [
                "00000000-0000-0000-0000-000000000000",
                "33333333-3333-3333-3333-333333333333",
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ],
            1,
        ),
        (
            ["TextSection", 2],
            {},
            [
                "00000000-0000-0000-0000-000000000000",
                "11111111-1111-1111-1111-111111111111",
                "33333333-3333-3333-3333-333333333333",
                "22222222-2222-2222-2222-222222222222",
            ],
            2,
        ),
        (
            ["TextSection", 3],
            {},
            [
                "00000000-0000-0000-0000-000000000000",
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
                "33333333-3333-3333-3333-333333333333",
            ],
            3,
        ),
        (
            ["TextSection", 4],
            {},
            [
                "00000000-0000-0000-0000-000000000000",
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
                "33333333-3333-3333-3333-333333333333",
            ],
            3,
        ),
        (
            ["TextSection", None],
            {},
            [
                "00000000-0000-0000-0000-000000000000",
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
                "33333333-3333-3333-3333-333333333333",
            ],
            3,
        ),
    ],
)
def test_addSection(fk, args, kwargs, res, lastpos):
    pg = fk.f_page()
    ids = [
        "00000000-0000-0000-0000-000000000000",
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
    ]
    new_id = "33333333-3333-3333-3333-333333333333"
    [fk.f_section(id=x, page=pg.id) for x in ids]
    p = Page.get(str(pg.id))
    a = p.model
    kwargs.update({"id": new_id})
    assert p.addSection(*args, kwargs)
    assert a._data["sections"] == res
    with db_session:
        new_secs_dict = [
            s.to_dict()
            for s in fk.db.Page[pg.id].sections.order_by(lambda x: x.position)
        ]
    new_secs_ids = [s["id"] for s in new_secs_dict]
    assert a._data["sections"] == new_secs_ids
    assert a.page.lastPosition == lastpos


def test_check_args_addsection():
    check_args(Page.addSection, [str], bool, slot_order=0)
    check_args(Page.addSection, [str, int, dict], bool, slot_order=1)


def test_append():
    with pytest.raises(NotImplementedError):
        PageModel.append("self")


@pytest.mark.parametrize(
    "func, format, ext",
    [("exportToPDF", "pdf:writer_pdf_Export", ".pdf"), ("exportToODT", "odt", ".odt")],
)
def test_exportTo(fk, func, format, ext):
    pg = fk.f_page()
    p = Page.get(str(pg.id))
    with patch("mycartable.classeur.convert.qrunnable") as w:
        getattr(p, func)()

        assert w.called
        assert w.call_args.args[1:] == (format, ext)
