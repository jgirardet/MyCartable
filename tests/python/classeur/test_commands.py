import pytest
from fixtures import compare_dict_list
from mycartable.classeur import Classeur, Page, Section
from mycartable.classeur.commands import AddSectionCommand, RemoveSectionCommand
from mycartable.classeur.sections.image import import_FILES
from pony.orm import db_session


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
            ("TextSection", {"text": "aaa"}, None, 1),
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
        self, fk, setup_page, qtbot, section, kwargs, after_redo, new_res, nb_ajoute
    ):
        p, secs, c, po = setup_page()
        entity = getattr(fk.db, section)
        img = None
        # tweak for image
        if "path" in kwargs:
            img = new_res(kwargs["path"])
            kwargs["path"] = str(img)

        # redo at init
        po.addSection(section, 1, kwargs)
        assert c.undoStack.command(0).text() == AddSectionCommand.formulations[section]
        assert po.model.count == 3 + nb_ajoute
        with db_session:
            assert entity.select().count() == nb_ajoute
            if "path" in kwargs:
                after_redo = {"path": entity.select().first().path}

        # undo
        po.classeur.undoStack.undo()
        assert po.model.count == 3
        with db_session:
            assert entity.select().count() == 0
            assert compare_dict_list(
                [x.to_dict() for x in fk.db.Section.select()],
                secs,
                exclude=["modified"],
            )

        # redo
        po.classeur.undoStack.redo()
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
            print(img)
            kwargs["path"] = str(img)
        p, secs, c, po = setup_page()
        im = Section.new_sub(page=p["id"], **kwargs, classtype=section)
        po = Page.get(p["id"], parent=c)
        entity = getattr(fk.db, section)

        # redo at init
        po.removeSection(3)
        assert (
            c.undoStack.command(0).text() == RemoveSectionCommand.formulations[section]
        )
        assert po.model.count == 3
        with db_session:
            assert entity.select().count() == 0

        # undo
        po.classeur.undoStack.undo()
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
                print(import_FILES() / item.path)
                assert (import_FILES() / item.path).read_bytes() == img.read_bytes()
            else:
                for k, v in after_redo.items():
                    assert getattr(item, k) == v

        # redo
        po.classeur.undoStack.redo()
        assert po.model.count == 3
        with db_session:
            assert entity.select().count() == 0
