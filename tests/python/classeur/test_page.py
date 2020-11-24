import pytest
from PySide2.QtCore import QModelIndex, Qt
from fixtures import ss, check_args
from mycartable.classeur import Page, PageModel, TextSection
from mycartable.package.utils import shift_list
from pony.orm import db_session, make_proxy


def test_subclassing(fk):
    ac = fk.f_activite()
    x = Page.new(activite=ac.id)
    y = Page.get(x.id)
    assert x == y
    assert x.delete()
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

    # matiere
    assert p.matiereId == str(ac.matiere.id)


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


@pytest.mark.parametrize(
    "nom, sectionclass",
    [("textSection", TextSection)],
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
    assert a.data(a.index(1, 0), 99999) is None


def test_rowCount(fk):
    pg = fk.f_page()
    fk.b_section(3, page=pg.id)
    p = Page.get(str(pg.id))
    a = p.model
    assert a.rowCount(QModelIndex()) == 3


def test_roleNames(fk):
    pg = fk.f_page()
    p = Page.get(str(pg.id))
    a = p.model
    assert PageModel.SectionRole in a.roleNames()


@pytest.mark.parametrize(
    "source, target",
    [
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (1, 0),
        (1, 1),
        (1, 2),
        (1, 3),
        (1, 4),
        (2, 0),
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (3, 0),
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (4, 0),
        (4, 1),
        (4, 2),
        (4, 3),
        (4, 4),
    ],
)
def test_move(fk, source, target):
    pg = fk.f_page()
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


@pytest.mark.parametrize(
    "idx, res",
    [
        (
            0,
            [
                "20d5d747-c3ea-4ebe-ab87-54159627ab98",
                "2ef38337-6e09-4394-8d46-d2be8161daeb",
            ],
        ),
        (
            1,
            [
                "a1258e33-7446-4681-8729-d1b09501d9b7",
                "2ef38337-6e09-4394-8d46-d2be8161daeb",
            ],
        ),
        (
            2,
            [
                "a1258e33-7446-4681-8729-d1b09501d9b7",
                "20d5d747-c3ea-4ebe-ab87-54159627ab98",
            ],
        ),
        (
            3,
            [
                "a1258e33-7446-4681-8729-d1b09501d9b7",
                "20d5d747-c3ea-4ebe-ab87-54159627ab98",
                "2ef38337-6e09-4394-8d46-d2be8161daeb",
            ],
        ),
    ],
)
def test_removeRows(fk, idx, res):
    pg = fk.f_page()
    ids = [
        "a1258e33-7446-4681-8729-d1b09501d9b7",
        "20d5d747-c3ea-4ebe-ab87-54159627ab98",
        "2ef38337-6e09-4394-8d46-d2be8161daeb",
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


@pytest.mark.parametrize(
    "args, kwargs, res",
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
        ),
    ],
)
def test_addSection(fk, args, kwargs, res):
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


def test_check_args_addsection():
    check_args(Page.addSection, [str], bool, slot_order=0)
    check_args(Page.addSection, [str, int, dict], bool, slot_order=1)


def test_append():
    with pytest.raises(NotImplementedError):
        PageModel.append("self")
