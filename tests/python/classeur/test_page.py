from datetime import datetime
from unittest.mock import patch

import pytest
from PyQt5.QtCore import QModelIndex, QObject
from mycartable.classeur.sections.image import import_FILES
from mycartable.defaults.roles import SectionRole
from tests.python.fixtures import ss, disable_log, compare_dict_list
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
    Classeur,
    AddSectionCommand,
    RemoveSectionCommand,
)
from mycartable.utils import shift_list
from pony.orm import db_session


def test_subclassing(fk, bridge):
    ac = fk.f_activite()
    x = Page.new(activite=ac.id, parent=bridge)
    y = Page.get(x.id, parent=bridge)
    assert x == y
    assert x.delete()
    with disable_log():
        assert Page.get(y.id) is None


@pytest.mark.freeze_time("2017-05-21")
def test_update_modified_if_viewed(fk, bridge, qtbot):
    class PPage(Page):
        entity_name = "Page"
        UPDATE_MODIFIED_DELAY = 0

    pa = fk.f_page(created=datetime(2000, 2, 2))
    p = PPage.get(pa.id, parent=bridge)
    with qtbot.waitSignal(p.pageModified):
        pass
    assert p._data["modified"] == "2017-05-21T00:00:00"


def test_properties(fk, bridge):
    ac = fk.f_activite()
    p = Page.new(titre="bla", activite=ac.id, lastPosition=5, parent=bridge)

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


def test_property_model(fk, bridge):
    ac = fk.f_activite()
    p = Page.new(activite=ac.id, parent=bridge)
    assert isinstance(p.model, PageModel)
    assert p.model.parent() == p


def test_base_init(fk, bridge):
    pg = fk.f_page(td=True)
    sections = pg.pop("sections")
    p = Page.get(pg["id"], parent=bridge)
    assert p.model._data == pg
    assert p.model.rowCount(QModelIndex()) == 0
    assert p.matiereId == p.matiere.id == pg["matiere"]
    assert [b.id for b in p.model._sections] == sections


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
def test_data_role(fk, bridge, nom, sectionclass):
    sec = getattr(fk, "f_" + nom)(td=True)
    p = Page.get(sec["page"], parent=bridge)
    a = p.model
    res = a.data(a.index(0, 0), SectionRole)
    assert isinstance(res, sectionclass)
    res2 = a.data(a.index(0, 0), SectionRole)
    assert res is res2
    assert res.id == sec["id"]
    assert res.classtype == sec["classtype"]
    # invalid index
    assert a.data(a.index(99, 99), SectionRole) is None
    # no good role
    assert a.data(a.index(0, 0), 99999) is None


def test_rowCount(fk, bridge):
    pg = fk.f_page()
    fk.b_section(3, page=pg.id)
    p = Page.get(str(pg.id), parent=bridge)
    a = p.model
    assert a.rowCount(QModelIndex()) == 3
    assert a.count == 3


def test_roleNames(fk, bridge):
    pg = fk.f_page()
    p = Page.get(str(pg.id), parent=bridge)
    a = p.model
    assert SectionRole in a.roleNames()


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
def test_move(fk, bridge, source, target, lastposition):
    pg = fk.f_page(lastPosition=9)
    secs_ids_pre = [str(x.id) for x in fk.b_section(3, page=pg.id)]
    p = Page.get(str(pg.id), parent=bridge)
    a = p.model
    new_order = shift_list(secs_ids_pre, source, 1, target)
    res = a.move(source, target)
    with db_session:
        new_secs_dict = [
            s.to_dict()
            for s in fk.db.Page[pg.id].sections.order_by(lambda x: x.position)
        ]
        new_secs_ids = [s["id"] for s in new_secs_dict]
        assert [b.id for b in a._sections] == new_secs_ids
    if res:
        assert new_secs_ids != secs_ids_pre
        assert new_secs_ids == new_order
    else:
        assert new_secs_ids == secs_ids_pre
    assert [s["position"] for s in new_secs_dict] == [0, 1, 2]
    assert [s.position for s in a._sections] == [0, 1, 2]
    assert a.page.lastPosition == lastposition


@pytest.mark.parametrize(
    "idx, res, lastpos, position_after",
    [
        (
            0,
            [
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ],
            0,
            [0, 1],
        ),
        (
            1,
            [
                "00000000-0000-0000-0000-000000000000",
                "22222222-2222-2222-2222-222222222222",
            ],
            1,
            [0, 1],
        ),
        (
            2,
            [
                "00000000-0000-0000-0000-000000000000",
                "11111111-1111-1111-1111-111111111111",
            ],
            1,
            [0, 1],
        ),
        (
            3,
            [
                "00000000-0000-0000-0000-000000000000",
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ],
            0,
            [0, 1, 2],
        ),
    ],
)
def test_removeRows(fk, bridge, qtbot, idx, res, lastpos, position_after, caplogger):
    pg = fk.f_page(lastPosition=0)
    ids = [
        "00000000-0000-0000-0000-000000000000",
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
    ]
    [fk.f_section(id=x, page=pg.id) for x in ids]
    p = Page.get(str(pg.id), parent=bridge)
    a = p.model
    # with qtbot.waitSignal(a.rowsRemoved):
    p.removeSection(idx)

    # instance dans le bon ordre
    assert [b.id for b in a._sections] == res

    # la position des Section instance est mise aussi à jour.
    assert [b.position for b in a._sections] == position_after

    with db_session:
        new_secs_dict = [
            s.to_dict()
            for s in fk.db.Page[pg.id].sections.order_by(lambda x: x.position)
        ]
    new_secs_ids = [s["id"] for s in new_secs_dict]
    assert [b.id for b in a._sections] == new_secs_ids
    assert position_after == [s["position"] for s in new_secs_dict]
    assert a.page.lastPosition == lastpos


# def test_check_args_addsection():
# check_args(Page.addSection, [str], bool, slot_order=0)
# check_args(Page.addSection, [str, int, dict], bool, slot_order=1)


def test_append():
    with pytest.raises(NotImplementedError):
        PageModel.append("self")


@pytest.mark.parametrize(
    "func, format, ext",
    [("exportToPDF", "pdf:writer_pdf_Export", ".pdf"), ("exportToODT", "odt", ".odt")],
)
def test_exportTo(fk, bridge, func, format, ext):
    pg = fk.f_page()
    p = Page.get(str(pg.id), parent=bridge)
    with patch("mycartable.classeur.convert.partial") as w:
        getattr(p, func)()

        assert w.called
        assert w.call_args.args[1:] == (format, ext)


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
def test_addSection(fk, bridge, args, kwargs, res, lastpos, qtbot):
    pg = fk.f_page()
    ids = [
        "00000000-0000-0000-0000-000000000000",
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
    ]
    new_id = "33333333-3333-3333-3333-333333333333"
    [fk.f_section(id=x, page=pg.id) for x in ids]
    p = Page.get(str(pg.id), parent=bridge)
    a = p.model
    kwargs.update({"id": new_id})
    with qtbot.waitSignal(a.rowsInserted):
        p.addSection(*args, kwargs)

    # les ids correspondent
    assert [b.id for b in a._sections] == res
    # la position des Section instance est mise aussi à jour.
    assert [b.position for b in a._sections] == [0, 1, 2, 3]
    with db_session:
        new_secs_dict = [
            s.to_dict()
            for s in fk.db.Page[pg.id].sections.order_by(lambda x: x.position)
        ]
    new_secs_ids = [s["id"] for s in new_secs_dict]
    assert [b.id for b in a._sections] == new_secs_ids
    assert a.page.lastPosition == lastpos


def new_page(fk):
    c = Classeur()
    p = fk.f_page()
    po = Page.get(p.id, parent=c)
    model = po.model
    return p, po, model, c


def test_addSection_text(fk, qtbot):
    p, po, model, c = new_page(fk)
    with qtbot.waitSignal(po.model.rowsInserted):
        po.addSection("TextSection", 0)
    assert model.count == 1
    assert model.data(model.index(0, 0), SectionRole).text == "<body></body>"


def test_addSection_image(
    fk,
    qtbot,
    png_annot,
):
    p, po, model, c = new_page(fk)
    with qtbot.waitSignal(po.model.rowsInserted):
        po.addSection("ImageSection", 0, {"path": str(png_annot)})
    assert model.count == 1
    new_img = model.data(model.index(0, 0), SectionRole).absolute_path
    assert new_img.read_bytes() == png_annot.read_bytes()


def test_addSection_image_pdf(
    fk,
    qtbot,
    resources,
):
    pdf = resources / "2pages.pdf"
    p, po, model, c = new_page(fk)
    fk.f_textSection(page=p.id)
    model._reset()  # ajoute la section
    with qtbot.waitSignal(po.model.rowsInserted):
        po.addSection("ImageSection", 1, {"path": str(pdf)})
    assert model.count == 3
    assert po.lastPosition == 1


def test_addSection_image_vide(
    fk,
    qtbot,
):
    p, po, model, c = new_page(fk)
    with qtbot.waitSignal(po.model.rowsInserted):
        po.addSection("ImageSection", 0, {"height": 1, "width": 1})
    assert model.count == 1
    new_img = model.data(model.index(0, 0), SectionRole).absolute_path
    assert new_img.is_file()


def test_addSection_equation(
    fk,
    qtbot,
):
    p, po, model, c = new_page(fk)
    with qtbot.waitSignal(po.model.rowsInserted):
        po.addSection("EquationSection", 0, {"content": "aaa"})
    assert model.count == 1
    assert model.data(model.index(0, 0), SectionRole).content == "aaa"


@pytest.mark.parametrize(
    "section, string, rows, columns",
    [
        (AdditionSection, "1+1", 4, 2),
        (SoustractionSection, "1-1", 3, 4),
        (MultiplicationSection, "1*1", 4, 2),
        (DivisionSection, "1/1", 3, 6),
    ],
)
def test_addSection_addition(
    section,
    string,
    rows,
    columns,
    fk,
    qtbot,
):
    p, po, model, c = new_page(fk)
    with qtbot.waitSignal(po.model.rowsInserted):
        po.addSection(section.entity_name, 0, {"string": string})
    assert model.count == 1
    res = model.data(model.index(0, 0), SectionRole)
    assert isinstance(res, section)
    assert res.rows == rows
    assert res.columns == columns


def test_addSection_tableau(
    fk,
    qtbot,
):
    p, po, model, c = new_page(fk)
    with qtbot.waitSignal(po.model.rowsInserted):
        po.addSection("TableauSection", 0, {"lignes": 3, "colonnes": 2})
    assert model.count == 1
    res = model.data(model.index(0, 0), SectionRole)
    assert isinstance(res, TableauSection)
    assert res.lignes == 3
    assert res.colonnes == 2


def test_addSection_frise(
    fk,
    qtbot,
):
    p, po, model, c = new_page(fk)
    with qtbot.waitSignal(po.model.rowsInserted):
        po.addSection("FriseSection", 0, {"height": 3})
    assert model.count == 1
    res = model.data(model.index(0, 0), SectionRole)
    assert isinstance(res, FriseSection)
    assert res.height == 3


class TestPageCommands:
    @pytest.fixture()
    def setup_page(self, fk):
        def wrap():
            p = fk.f_page(td=True)
            secs = fk.b_section(3, page=p["id"], td=True)
            c = Classeur()
            po = Page.get(p["id"], parent=c)
            return p, secs, c, po

        return wrap

    @pytest.mark.parametrize(
        "section, kwargs, after_redo, nb_ajoute",
        [
            ("TextSection", {"text": "<body></body>"}, None, 1),
            ("EquationSection", {"content": "aaa"}, None, 1),
            (
                "AdditionSection",
                {"string": "1+2"},
                {"datas": ["", "", "", "1", "+", "2", "", ""], "size": 8, "virgule": 0},
                1,
            ),
            (
                "MultiplicationSection",
                {"string": "1*2"},
                {
                    "datas": ["", "", "", "2", "x", "1", "", ""],
                    "size": 8,
                    "virgule": 0,
                },
                1,
            ),
            (
                "SoustractionSection",
                {"string": "2-1"},
                {
                    "datas": ["", "", "2", "", "-", "", "1", "", "", "", "", ""],
                    "size": 12,
                    "virgule": 0,
                },
                1,
            ),
            (
                "DivisionSection",
                {"string": "2/1"},
                {
                    "dividende": "2",
                    "diviseur": "1",
                    "quotient": "",
                },
                1,
            ),
            ("TableauSection", {"lignes": 3, "colonnes": 2}, None, 1),
            ("FriseSection", {"height": 3, "titre": "aa"}, None, 1),
            ("ImageSection", {"path": "sc1.png"}, None, 1),
            ("ImageSection", {"path": "pdf7pages.pdf"}, None, 7),
            ("ImageSection", {"height": 1, "width": 1}, {"path": "ze"}, 1),
        ],
    )
    def test_AddSectionCommand(
        self,
        request,
        fk,
        setup_page,
        qtbot,
        section,
        kwargs,
        after_redo,
        new_res,
        nb_ajoute,
    ):
        p, secs, c, po = setup_page()
        stack = po.undoStack
        entity = getattr(fk.db, section)
        img = None
        # tweak for image
        if "path" in kwargs:
            img = new_res(kwargs["path"])
            kwargs["path"] = str(img)

        # redo at init
        po.addSection(section, 1, kwargs)
        new_sec = po.get_section(1)
        assert new_sec.undoStack.count() == 0
        assert new_sec.undoStack.parent() == new_sec
        assert (
            stack.command(stack.count() - 1).text()
            == AddSectionCommand.formulations[section]
        )
        assert po.model.count == 3 + nb_ajoute
        with db_session:
            assert entity.select().count() == nb_ajoute
            if "path" in kwargs:
                after_redo = {"path": entity.select().first().path}

        backup1 = po.get_section(3).backup()

        # undo
        stack.undo()
        assert po.model.count == 3
        with db_session:
            assert entity.select().count() == 0
            assert compare_dict_list(
                [x.to_dict() for x in fk.db.Section.select()],
                secs,
                exclude=[("modified",)],
            )

        # redo
        stack.redo()
        assert po.model.count == 3 + nb_ajoute
        after_redo = after_redo or kwargs
        with db_session:
            assert entity.select().count() == nb_ajoute
            item = entity.select().first()
            if "path" in after_redo:
                if nb_ajoute < 2 and img:  # on test pas les pdf et pas les vides
                    assert (import_FILES() / item.path).read_bytes() == img.read_bytes()
            else:
                for k, v in after_redo.items():
                    assert getattr(item, k) == v

        if request.node.name != "test_AddSectionCommand[ImageSection-kwargs9-None-7]":
            # marche avec pdf mais plus compliqué à tester
            backup1.pop("modified")
            backup2 = po.get_section(3).backup()
            backup2.pop("modified")
            assert backup1 == backup2

    @pytest.mark.parametrize(
        "section, kwargs, after_redo",
        [
            ("TextSection", {"text": "aaa"}, {"text": "aaa"}),
            ("EquationSection", {"content": "aaa"}, {"content": "aaa"}),
            (
                "AdditionSection",
                {"string": "1+2"},
                {"datas": ["", "", "", "1", "+", "2", "", ""], "size": 8, "virgule": 0},
            ),
            (
                "MultiplicationSection",
                {"string": "1*2"},
                {
                    "datas": ["", "", "", "2", "x", "1", "", ""],
                    "size": 8,
                    "virgule": 0,
                },
            ),
            (
                "SoustractionSection",
                {"string": "2-1"},
                {
                    "datas": ["", "", "2", "", "-", "", "1", "", "", "", "", ""],
                    "size": 12,
                    "virgule": 0,
                },
            ),
            (
                "DivisionSection",
                {"string": "2/1"},
                {
                    "dividende": "2",
                    "diviseur": "1",
                    "quotient": "",
                },
            ),
            (
                "TableauSection",
                {"lignes": 3, "colonnes": 2},
                {"lignes": 3, "colonnes": 2},
            ),
            (
                "FriseSection",
                {"height": 3, "titre": "aa"},
                {"height": 3, "titre": "aa"},
            ),
            ("ImageSection", {"path": "sc1.png"}, {}),
        ],
    )
    def test_RemoveSectionCommand(
        self, fk, setup_page, qtbot, section, kwargs, after_redo, new_res
    ):

        # tweak for image
        img = None
        if "path" in kwargs:
            img = new_res(kwargs["path"])
            kwargs["path"] = str(img)
        p, secs, c, po = setup_page()
        im = Section.new_sub(page=p["id"], **kwargs, classtype=section, parent=po)
        po = Page.get(p["id"], parent=c)
        stack = po.undoStack
        entity = getattr(fk.db, section)

        backup1 = po.get_section(3).backup()
        # redo at init
        po.removeSection(3)
        assert (
            stack.command(stack.count() - 1).text()
            == RemoveSectionCommand.formulations[section]
        )
        assert po.model.count == 3
        with db_session:
            assert entity.select().count() == 0

        # undo
        stack.undo()
        assert po.model.count == 4
        with db_session:
            assert entity.select().count() == 1
            assert compare_dict_list(
                [x.to_dict() for x in fk.db.Section.select()],
                secs,
                exclude=["modified"],
            )
            item = entity.select().first()
            if "path" in after_redo:
                assert (import_FILES() / item.path).read_bytes() == img.read_bytes()
            else:
                for k, v in after_redo.items():
                    assert getattr(item, k) == v

        backup1.pop("modified")
        backup2 = po.get_section(3).backup()
        backup2.pop("modified")
        assert backup1 == backup2

        # redo
        stack.redo()
        assert po.model.count == 3
        with db_session:
            assert entity.select().count() == 0
