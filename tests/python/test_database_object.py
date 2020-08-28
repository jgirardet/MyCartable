import uuid

import pytest
from PIL import Image
from PySide2.QtCore import QUrl, Qt
from fixtures import check_args
from package import constantes
from package.database_mixins.matiere_mixin import MatieresDispatcher
from package.database_object import DatabaseObject
from factory import *
from unittest.mock import patch, call
from package.files_path import FILES
from package.page import text_section
from loguru_caplog import loguru_caplog as caplog  # used in tests
from pony.orm import ObjectNotFound


class TestPageMixin:
    def test_init(self, dao):
        assert dao._currentPage == 0
        assert dao._currentTitre == ""
        assert dao._currentEntry == None

        assert dao.timer_titre.isSingleShot()

    def test_newPage(self, dao, qtbot):
        f = f_page()  # pour avoir plusieurs dans le resultats
        with qtbot.wait_signal(dao.newPageCreated, timeout=100):
            r = dao.newPage(f.activite.id)

    def test_currentPage(self, dao, qtbot):
        a = f_page()
        b = f_page()
        assert dao.currentPage == 0

        # setCurrentPage
        dao.currentPage = 1
        assert dao.currentPage == a.id
        with qtbot.wait_signal(dao.currentPageChanged, timeout=100):
            dao.currentPage = 2
        assert dao.currentPage == dao.currentPage

        # set currentpage do nothing if same id
        with qtbot.assertNotEmitted(dao.currentPageChanged):
            dao.currentPage = 2
        assert dao.currentPage == b.id

        # set currentpage do nothing if same id
        with qtbot.assertNotEmitted(dao.currentPageChanged):
            dao.currentPage = 2
        assert dao.currentPage == b.id

    def test_current_entry(self, dao):
        a = f_page()
        dao.currentPage = 1
        with db_session:
            assert (
                dao._currentEntry.titre
                == a.titre
                == dao._currentTitre
                == dao.currentTitre
            )

    def test_CurrentTitreSet(self, dao):
        b_page(2)

        # case no current page
        dao.currentTitre = "omk"
        assert dao._currentTitre == ""
        dao.currentPage = 1
        with patch.object(dao.timer_titre, "start") as m:
            dao.currentTitre = "mokmk"
            assert dao.currentTitre == "mokmk"
            assert m.call_args_list == [call(500)]

            # do not call storage if same value
            dao.currentTitre = "mokmk"
            assert m.call_args_list == [call(500)]

    def test_UnderscoreCurrentTitreSet(self, dao, qtbot):
        f_page()
        dao.currentPage = 1
        dao.TITRE_TIMER_DELAY = 0
        with qtbot.wait_signal(dao.currentTitreChanged):
            dao.currentTitre = "aaa"
        with db_session:
            assert dao.db.Page[1].titre == "aaa"

    def test_setCurrentTitre(self, dao, qtbot):
        f_page()
        dao.currentPage = 1
        dao.TITRE_TIMER_DELAY = 0
        with qtbot.assertNotEmitted(dao.currentTitreChanged):
            dao.setCurrentTitre("blabla")
        assert dao.currentTitre == "blabla"

        with qtbot.waitSignal(dao.currentTitreSetted):
            dao.setCurrentTitre("ble")

        # no curerntPage
        dao.currentPage = 0
        with qtbot.assertNotEmitted(dao.currentTitreSetted):
            dao.setCurrentTitre("blabla")

    def test_on_pagechanged_reset_model(self, dao):
        p1 = f_page()
        f_section(page=p1.id)
        dao.currentPage = p1.id
        with db_session:
            assert dao.pageModel.page.id == p1.id

    def test_removePAge(self, dao, qtbot):
        f_page()
        dao.removePage(1)
        with db_session:
            assert not dao.db.Page.get(id=1)
        assert dao.currentPage == 0

    def test_removePAge_no_item_in_db(self, dao, qtbot):
        dao.removePage(99)
        assert dao.currentPage == 0

    def test_removePAge_blanck_if_currentItem(self, dao):
        f_page()
        dao.currentPage = 1
        dao.removePage(1)
        assert dao.currentPage == 0

    def test_allow_currentPAge_can_be_0(self, dao):
        f_page()
        dao.currentPage = 1
        dao.currentPage = 0

    def test_exportToPdf(selfsekf, dao):
        f_page(titre="blà")
        dao.currentPage = 1
        with patch("package.database_mixins.page_mixin.QDesktopServices.openUrl") as m:
            with patch("package.database_mixins.page_mixin.soffice_convert") as v:
                dao.exportToPDF()
                v.assert_called_with(1, "pdf:writer_pdf_Export", "bla.pdf", dao.ui)
                m.assert_called_with(v.return_value.as_uri())

    def test_exportToOdt(selfsekf, dao):
        f_page(titre="blà")
        dao.currentPage = 1
        with patch("package.database_mixins.page_mixin.QDesktopServices.openUrl") as m:
            with patch("package.database_mixins.page_mixin.soffice_convert") as v:
                dao.exportToOdt()
                v.assert_called_with(1, "odt", "bla.odt", dao.ui)
                m.assert_called_with(v.return_value.as_uri())


class TestMatiereMixin:
    def create_matiere(self):
        gp = f_groupeMatiere(annee=2019)

        def activ(mat):
            f_activite(nom="un", matiere=mat)
            f_activite(nom="deux", matiere=mat)
            f_activite(nom="trois", matiere=mat)

        f_matiere("un", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id)
        activ(1)
        f_matiere("deux", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id)
        activ(2)
        f_matiere("trois", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id)
        activ(3)
        f_matiere("quatre", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id)
        activ(4)

    def test_init(self, dao):

        assert dao._currentMatiere == 0

    def test_currentMatiere(self, dao, qtbot):
        self.create_matiere()
        dao.init_matieres()
        assert dao.currentMatiere == 0

        # from int
        with qtbot.waitSignal(dao.currentMatiereChanged, timeout=100):
            dao.currentMatiere = 2
        dao.currentMatiere = 2  # same
        assert dao.currentMatiere == 2
        dao.currentMatiere = "fez"  # not in do nothing
        assert dao.currentMatiere == 2

        # from index
        with qtbot.waitSignal(dao.matiereReset):
            dao.setCurrentMatiereFromIndex(2)
        assert dao.currentMatiere == 3

        # get index from id
        assert dao.getMatiereIndexFromId(3) == 2
        assert dao.getMatiereIndexFromId(99999) is 0

    def test_currentMatiereItem(self, dao):
        m = f_matiere(td=True)
        dao.currentMatiere = m["id"]
        assert dao.currentMatiereItem == m

    def test_matiereList(self, dao):
        self.create_matiere()
        dao.init_matieres()

        # listnom
        reslist = [
            {
                "activites": [1, 2, 3],
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "id": 1,
                "groupe": 1,
                "nom": "un",
                "position": 0,
            },
            {
                "activites": [4, 5, 6],
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": 1,
                "id": 2,
                "nom": "deux",
                "position": 1,
            },
            {
                "activites": [7, 8, 9],
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": 1,
                "id": 3,
                "nom": "trois",
                "position": 2,
            },
            {
                "activites": [10, 11, 12],
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": 1,
                "id": 4,
                "nom": "quatre",
                "position": 3,
            },
        ]
        assert dao.matieresList == reslist

        # refresh
        f_matiere(
            "cinq",
            groupe=f_groupeMatiere(annee=2019),
            _fgColor=4294967295,
            _bgColor=4294901760,
        )
        f_activite(matiere=5)
        f_activite(matiere=5)
        f_activite(matiere=5)
        dao.matieresListRefresh()
        reslist.append(
            {
                "activites": [13, 14, 15],
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": 2,
                "id": 5,
                "nom": "cinq",
                "position": 0,
            }
        )
        assert dao.matieresList == reslist

    def test_pagesParSection(self, dao):
        assert dao.pagesParSection == []
        b_activite(3)
        p = f_page(td=True, activite=3)
        dao.currentMatiere = 1
        assert dao.pagesParSection[0]["id"] == 1
        assert dao.pagesParSection[1]["id"] == 2
        assert dao.pagesParSection[2]["id"] == 3
        assert dao.pagesParSection[2]["pages"] == [p]

    def test_matiere_dispatch(self, ddbr):
        # anne n'exist pas
        with pytest.raises(ObjectNotFound):
            MatieresDispatcher(ddbr, 2000)
        # assert m.annee.id == 2000

        # anne existe
        f_annee(1954)
        m = MatieresDispatcher(ddbr, 1954)
        assert m.annee.id == 1954

    def test_peuplerLesMatieresPArDefault(self, dao):
        with db_session:
            assert Matiere.select().count() == 0
            assert GroupeMatiere.select().count() == 0

        dao.peuplerLesMatieresParDefault(dao.anneeActive)

        with db_session:
            assert Matiere.select().count() == len(MATIERES)
            assert GroupeMatiere.select().count() == len(MATIERE_GROUPE)

        assert len(dao.matieresList) == len(MATIERES)


class TestActiviteMixin:
    def test_getDeplacePageModel(self, dao):
        g1 = f_groupeMatiere(annee=1900)
        g2 = f_groupeMatiere(annee=2000)
        m1 = f_matiere(nom="un", groupe=g1)
        m2 = f_matiere(nom="deux", groupe=g1)
        m3 = f_matiere(nom="trois", groupe=g2, bgColor="red")
        m4 = f_matiere(nom="quatre", groupe=g2, bgColor="blue")
        for i in [m1, m2, m3, m4]:
            b_activite(3, nom="rien", matiere=i.id)
        res = dao.getDeplacePageModel(2000)
        assert res == [
            {
                "activites": [
                    {"id": 7, "nom": "rien"},
                    {"id": 8, "nom": "rien"},
                    {"id": 9, "nom": "rien"},
                ],
                "bgColor": QColor("red"),
                "nom": "trois",
            },
            {
                "activites": [
                    {"id": 10, "nom": "rien"},
                    {"id": 11, "nom": "rien"},
                    {"id": 12, "nom": "rien"},
                ],
                "bgColor": QColor("blue"),
                "nom": "quatre",
            },
        ]

    def test_changeActivite(self, dao, qtbot):
        f_activite()
        a = f_page()
        with db_session:
            assert Page[1].activite.id == 2
        with qtbot.waitSignal(dao.pageActiviteChanged):
            dao.changeActivite(1, 1)
        with db_session:
            assert Page[1].activite.id == 1


class TestRecentsMixin:
    def test_init(self, dao, ddbn):
        a = b_page(5)
        with db_session:
            ddbn.Page.recents == dao.recentsModel


class TestLayoutMixin:
    def test_getlayoutsize(self, dao: DatabaseObject):
        assert (
            dao.getLayoutSizes("preferredCentralWidth")
            == constantes.preferredCentralWidth
        )

    def test_setStyle(self, dao: DatabaseObject, caplog):
        check_args(dao.setStyle, (int, dict), dict)
        a = f_style()

        # normal
        r = dao.setStyle(a.styleId, {"underline": True, "bgColor": "red"})
        assert r == {
            "bgColor": QColor("red"),
            "family": "",
            "fgColor": QColor("black"),
            "styleId": 1,
            "pointSize": None,
            "strikeout": False,
            "underline": True,
            "weight": None,
        }

        with db_session:
            item = dao.db.Style[a.styleId]
            assert item.bgColor == "red"
            assert item.underline == True

        # bad params
        r = dao.setStyle(a.styleId, {"badparam": True})
        assert "Unknown attribute 'badparam'" in caplog.records[0].msg
        assert caplog.records[0].levelname == "ERROR"
        caplog.clear()

        # style does not exists
        with db_session:
            b = dao.db.Style[a.styleId]
            b.delete()

        r = dao.setStyle(a.styleId, {"underline": True})
        assert (
            caplog.records[0].msg
            == "Echec de la mise à jour du style : ObjectNotFound  Style[1]"
        )
        assert caplog.records[0].levelname == "ERROR"

    def test_color_property(self, dao):
        assert dao.colorFond == QColor(130, 134, 138)
        assert dao.colorMainMenuBar == QColor(83, 93, 105)
        assert dao.colorPageToolBar == QColor(197, 197, 197)

    def test_font_property(self, dao):
        assert dao.fontMain == "Verdana"


class TestSectionMixin:
    def test_checkargs(self, dao):
        check_args(dao.loadSection, str, dict)
        check_args(dao.addSection, [str, dict], str)

    def test_loadsection_image(self, dao):
        s = f_imageSection(path="bla/ble.jpg")
        res = dao.loadSection(s.id)
        assert res["id"] == str(s.id)
        assert res["path"] == QUrl.fromLocalFile(str(FILES / "bla/ble.jpg"))

    def test_loadsection_image_false(self, dao):
        res = dao.loadSection(99999)
        assert res == {}

    def test_load_section_Operation(self, dao):
        a = f_additionSection(string="3+4")
        assert dao.loadSection(a.id) == {
            "classtype": "AdditionSection",
            "created": a.created.isoformat(),
            "datas": ["", "", "", "3", "+", "4", "", ""],
            "rows": 4,
            "columns": 2,
            "id": str(a.id),
            "modified": a.modified.isoformat(),
            "page": 1,
            "position": 0,
            "size": 8,
            "virgule": 0,
        }

    def test_load_section_tableau(self, dao):
        a = f_tableauSection(lignes=3, colonnes=3)
        assert dao.loadSection(a.id) == {
            "classtype": "TableauSection",
            "created": a.created.isoformat(),
            "colonnes": 3,
            "id": str(a.id),
            "lignes": 3,
            "modified": a.modified.isoformat(),
            "page": 1,
            "position": 0,
        }

    def test_loadsection_equation(self, dao):
        eq = f_equationSection(content="1+2", td=True)
        assert dao.loadSection(eq["id"]) == {
            "classtype": "EquationSection",
            "created": eq["created"],  # .created.isoformat(),
            "content": "1+2",
            "id": eq["id"],
            "modified": eq["modified"],  # a.modified.isoformat(),
            "page": 1,
            "position": 0,
            "curseur": 0,
        }

    @pytest.mark.parametrize(
        "page, content, res, signal_emitted",
        [
            (1, {"classtype": "TextSection"}, 1, True),
            # (1, {"classtype": "ImageSection"}, 0, True),
            (1, {"classtype": "EquationSection"}, 1, True),
            (1, {"classtype": "OperationSection", "string": "3+4"}, 1, True),
            (
                1,
                {"classtype": "OperationSection", "string": "3(4"},
                0,
                False,
            ),  # string invalide
            (1, {"string": "3+4"}, 0, False),
            (1, {"classtype": "OperationSection", "string": "4*3"}, 1, True),
            (1, {"classtype": "OperationSection", "string": "4-3"}, 1, True),
            (1, {"classtype": "OperationSection", "string": "4/3"}, 1, True),
            (1, {"classtype": "OperationSection", "string": "4/a"}, 0, False),
            (1, {"classtype": "TableauSection", "lignes": 3, "colonnes": 2}, 1, True),
        ],
    )
    def test_addSection(self, dao, ddbn, qtbot, page, content, res, signal_emitted):
        x = f_page()
        dao.pageModel.slotReset(x.id)
        if signal_emitted:
            with qtbot.waitSignal(dao.sectionAdded):
                a = dao.addSection(page, content)
        else:
            a = dao.addSection(page, content)
        with db_session:
            if res:
                _res = item = str(ddbn.Section.select().first().id)
                res = _res
            else:
                res = ""
        assert a == res
        if res == "":
            return
        with db_session:
            item = ddbn.Section.select().first()
            assert item.page.id == x.id
            for i in content.keys():
                if i == "string":
                    item.datas == create_operation(content["string"])
                else:
                    assert content[i] == getattr(item, i)

    @pytest.mark.parametrize(
        "page, content, res, signal_emitted",
        [
            (1, {"path": "png_annot", "classtype": "ImageSection",}, 1, True,),
            (1, {"path": QUrl("no/existe"), "classtype": "ImageSection",}, 0, False,),
            (1, {"path": "createOne", "classtype": "ImageSection",}, 1, True,),
            (1, {"path": QUrl("createOne"), "classtype": "ImageSection",}, 1, True,),
            (1, {"path": None, "classtype": "ImageSection",}, 0, False,),
            (1, {"path": "my/path", "classtype": "ImageSection"}, 0, False),
            (1, {"path": "lepdf", "classtype": "ImageSection",}, 1, True,),
        ],
    )
    def test_addSectionFile(
        self,
        png_annot,
        resources,
        dao,
        ddbr,
        qtbot,
        page,
        content,
        res,
        signal_emitted,
        tmpfile,
    ):
        x = f_page()
        dao.pageModel.slotReset(x.id)
        if "path" not in content:
            pass
        if content["path"] == "png_annot":
            content["path"] = str(png_annot)
        elif content["path"] == "lepdf":
            content["path"] = str(resources / "2pages.pdf")
        elif isinstance(content["path"], QUrl):
            if content["path"].toString() == "createOne":
                content["path"] = QUrl.fromLocalFile(str(tmpfile))
        elif content["path"] == "createOne":
            content["path"] = str(tmpfile)
        if signal_emitted:
            with qtbot.waitSignal(dao.sectionAdded):
                a = dao.addSection(page, content)
        else:
            a = dao.addSection(page, content)

        with db_session:
            if res:
                _res = item = str(ddbr.Section.select().first().id)
                res = _res
            else:
                res = ""
        assert a == res
        if res == "":
            return
        with db_session:
            item = ddbr.Section.select().first()
            assert item.page.id == x.id
            for i in content.keys():
                if i == "path":
                    assert content[i] == getattr(item, i)
                    assert (FILES / item.path).exists()
                elif i == "string":
                    item.datas == create_operation(content["string"])
                else:
                    assert content[i] == getattr(item, i)


class TestEquationMixin:
    def test_update(self, dao, qtbot):
        e = f_equationSection(content=" \n1\n ")
        event = json.dumps({"key": int(Qt.Key_2), "text": "2", "modifiers": None})
        with qtbot.waitSignal(dao.equationChanged):
            res = dao.updateEquation(e.id, " \n1\n ", 3, event)
        assert res == {"content": "  \n12\n  ", "curseur": 5}

    def test_isequationfocusable(self, dao):
        assert not dao.isEquationFocusable("  \n1 \n  ", 0)
        assert dao.isEquationFocusable("  \n1 \n  ", 4)


class TestImageSectionMixin:
    @pytest.mark.freeze_time("2344-9-21 7:48:5")
    def test_new_image_path(self, dao):
        with patch(
            "package.utils.uuid.uuid4",
            new=lambda: uuid.UUID("d9ca35e1-0b4b-4d42-9f0d-aa07f5dbf1a5"),
        ):
            dao.annee_active = 2019
            assert (
                dao.get_new_image_path(".jpg") == "2019/2344-09-21-07-48-05-d9ca3.jpg"
            )
            dao.annee_active = 2018
            assert (
                dao.get_new_image_path(".gif") == "2018/2344-09-21-07-48-05-d9ca3.gif"
            )

    def test_store_new_file_pathlib(self, resources, dao):
        obj = resources / "sc1.png"
        res = dao.store_new_file(obj)
        assert (dao.files / res).read_bytes() == obj.read_bytes()

    def test_store_new_file_str(self, resources, dao):
        obj = resources / "sc1.png"
        res = dao.store_new_file(str(obj))
        assert (dao.files / res).read_bytes() == obj.read_bytes()

    def test_pivoter_image(self, new_res, dao, qtbot):
        file = new_res("test_pivoter.png")
        img = Image.open(file)
        assert img.height == 124
        assert img.width == 673

        f = f_imageSection(path=str(file))
        with qtbot.waitSignal(dao.imageChanged):
            dao.pivoterImage(f.id, 1)
        img = Image.open(file)
        assert img.height == 673
        assert img.width == 124

    trait_600_600 = "data:image/png;base64,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"
    trait_600_600_as_png = "2019/2019-05-21-12-00-01-349bd.png"

    def test_annotationTextBGOpacity(self, dao):
        assert dao.annotationTextBGOpacity == 0.5


class TestTableauMixin:
    def test_check_args(self, dao):
        check_args(dao.initTableauDatas, str, list)
        check_args(dao.updateCell, [str, int, int, dict])
        check_args(dao.nbColonnes, str, int)
        check_args(dao.insertRow, [str, int])
        check_args(dao.appendRow, str)
        check_args(dao.insertColumn, [str, int])
        check_args(dao.appendColumn, str)
        check_args(dao.removeColumn, [str, int])
        check_args(dao.removeRow, [str, int])

    def test_init_datas(self, dao):
        x = f_tableauSection(3, 4)

        with db_session:
            assert dao.initTableauDatas(str(x.id)) == [
                x.to_dict() for x in TableauSection[x.id].get_cells()
            ]

    def test_updat_cell(self, dao, qtbot):
        x = f_tableauCell(x=2, y=3, texte="zer")

        with qtbot.waitSignal(dao.tableauChanged):
            dao.updateCell(x.tableau.id, 3, 2, {"texte": "bla"})
        with db_session:
            assert TableauCell[x.tableau.id, 3, 2].texte == "bla"

    def test_tableaulayoutchanged(self, dao, qtbot):
        with qtbot.waitSignal(dao.tableauChanged):
            dao.tableauLayoutChanged.emit()

    @pytest.mark.parametrize(
        "fn, lignes, colonnes",
        [
            ("insertRow", 3, 2),
            ("insertColumn", 2, 3),
            ("removeRow", 1, 2),
            ("removeColumn", 2, 1),
        ],
    )
    def test_add_remove_row_column(self, dao, qtbot, fn, lignes, colonnes):
        x = f_tableauSection(2, 2)
        with qtbot.waitSignal(dao.tableauLayoutChanged):
            getattr(dao, fn)(x.id, 1)
        with db_session:
            x = TableauSection[x.id]
            assert x.lignes == lignes
            assert x.colonnes == colonnes

    @pytest.mark.parametrize(
        "fn, lignes, colonnes", [("appendColumn", 2, 3), ("appendRow", 3, 2),],
    )
    def test_append_row_column(self, dao, qtbot, fn, lignes, colonnes):
        x = f_tableauSection(2, 2)
        with qtbot.waitSignal(dao.tableauLayoutChanged):
            getattr(dao, fn)(x.id)
        with db_session:
            x = TableauSection[x.id]
            assert x.lignes == lignes
            assert x.colonnes == colonnes

    def test_nb_colonnes(self, dao):
        x = f_tableauSection(2, 6)
        assert dao.nbColonnes(x.id) == 6


class TestTextSectionMixin:
    def test_check_args(self, dao):
        check_args(dao.updateTextSectionOnKey, [str, str, int, int, int, str], dict)
        check_args(dao.updateTextSectionOnChange, [str, str, int, int, int], dict)
        check_args(dao.updateTextSectionOnMenu, [str, str, int, int, int, dict], dict)
        check_args(dao.loadTextSection, str, dict)
        check_args(dao.getTextSectionColor, str, QColor)

    def test_updateTextSectionOnKey(self, dao):
        f_textSection(text="bla")
        dic_event = {"key": int(Qt.Key_B), "modifiers": int(Qt.ControlModifier)}
        event = json.dumps(dic_event)
        args = 1, "bla", 3, 3, 3

        with patch("package.database_mixins.text_mixin.TextSectionEditor") as m:
            res = dao.updateTextSectionOnKey(*args, event)
            m.assert_called_with(*args)
            m.return_value.onKey.assert_called_with(dic_event)
            assert res == m.return_value.onKey.return_value

    def test_updateTextSectionOnChange(self, dao, qtbot):
        f_textSection(text="bla")
        dic_event = {"key": int(Qt.Key_B), "modifiers": int(Qt.ControlModifier)}
        args = 1, "blap", 3, 3, 4

        with patch("package.database_mixins.text_mixin.TextSectionEditor") as m:
            with qtbot.waitSignal(dao.textSectionChanged):
                res = dao.updateTextSectionOnChange(*args)
            m.assert_called_with(*args)
            m.return_value.onChange.assert_called_with()
            assert res == m.return_value.onChange.return_value

    def test_updateTextSectionOnMenu(self, dao):
        f_textSection()
        dic_params = {"ble": "bla"}
        # params = json.dumps(dic_params)
        args = 1, "bla", 3, 3, 3

        with patch("package.database_mixins.text_mixin.TextSectionEditor") as m:
            res = dao.updateTextSectionOnMenu(*args, dic_params)
            m.assert_called_with(*args)
            m.return_value.onMenu.assert_called_with(ble="bla")
            assert res == m.return_value.onMenu.return_value

    def test_loadTextSection(self, dao):
        f_textSection()

        with patch("package.database_mixins.text_mixin.TextSectionEditor") as m:
            res = dao.loadTextSection(1)
            m.assert_called_with(1)
            m.return_value.onLoad.assert_called_with()
            assert res == m.return_value.onLoad.return_value

    def test_getTextSectionColor(self, dao):

        for x in ["red", "blue", "green", "black"]:
            assert dao.getTextSectionColor(x) == QColor(
                getattr(text_section, x.upper())
            )


class TestSessionMixin:
    @db_session
    def test_init_user(self, dao):
        assert dao.init_user() == {
            "id": 1,
            "last_used": 2019,
            "nom": "lenom",
            "prenom": "leprenom",
        }
        Utilisateur.user().delete()
        assert dao.init_user() == {}

    def test_newUser(self, dao, qtbot):
        check_args(dao.newUser, [str, str])

        # existe déja
        with pytest.raises(AssertionError):
            dao.newUser(nom="oj", prenom="omj")

        # n'existe pas
        with db_session:
            Utilisateur.user().delete()

        with qtbot.waitSignal(dao.currentUserChanged):
            dao.newUser(nom="oj", prenom="omj")
        assert dao.currentUser == {
            "id": 2,
            "last_used": 0,
            "nom": "oj",
            "prenom": "omj",
        }
        assert dao.currentUser == dao.current_user

    def test_newAnnee(self, dao):
        check_args(dao.newAnnee, [int, str])
        dao.newAnnee(2050, "ce3")
        with db_session:
            an = Annee[2050]
            assert an.niveau == "ce3"
            assert an.user == Utilisateur.user()

    def test_getMenuesAnnees(self, dao):
        check_args(dao.getMenuAnnees, None, list)
        with db_session:
            user = dao.db.Utilisateur.select().first()
        for i in range(4):
            f_annee(2016 - (i * i), user=user.id)  # pour tester l'ordre
        assert dao.getMenuAnnees() == [
            {"id": 2007, "niveau": "cm2007", "user": 1},
            {"id": 2012, "niveau": "cm2012", "user": 1},
            {"id": 2015, "niveau": "cm2015", "user": 1},
            {"id": 2016, "niveau": "cm2016", "user": 1},
            {
                "id": 2019,
                "niveau": "cm2019",
                "user": 1,
            },  # 2019 setté dans la fixture dao
        ]

    def test_anneActive(self, dao):
        assert dao.anneeActive == 2019


class TestChangeMatieresMixin:
    def test_get_activites(self, dao):
        b_activite(3, nom="rien")
        b_page(3, activite=1)
        assert dao.getActivites(1) == [
            {"id": 1, "matiere": 1, "nom": "rien", "position": 0, "nbPages": 3},
            {"id": 2, "matiere": 1, "nom": "rien", "position": 1, "nbPages": 0},
            {"id": 3, "matiere": 1, "nom": "rien", "position": 2, "nbPages": 0},
        ]

    def test_moveActivite(self, dao):
        b_activite(3, nom="rien")
        assert dao.moveActiviteTo(3, 0) == [
            {"id": 3, "matiere": 1, "nom": "rien", "position": 0, "nbPages": 0},
            {"id": 1, "matiere": 1, "nom": "rien", "position": 1, "nbPages": 0},
            {"id": 2, "matiere": 1, "nom": "rien", "position": 2, "nbPages": 0},
        ]

    def test_removeActivite(self, dao):
        b_activite(3, nom="rien")
        assert dao.removeActivite(2) == [
            {"id": 1, "matiere": 1, "nom": "rien", "position": 0, "nbPages": 0},
            {"id": 3, "matiere": 1, "nom": "rien", "position": 1, "nbPages": 0},
        ]

    def test_addActivite_par_activiteId(self, dao):
        b_activite(3, nom="rien")
        assert dao.addActivite(1) == [
            {"id": 4, "matiere": 1, "nom": "nouvelle", "position": 0, "nbPages": 0},
            {"id": 1, "matiere": 1, "nom": "rien", "position": 1, "nbPages": 0},
            {"id": 2, "matiere": 1, "nom": "rien", "position": 2, "nbPages": 0},
            {"id": 3, "matiere": 1, "nom": "rien", "position": 3, "nbPages": 0},
        ]

    def test_addActivite_par_matiereId(self, dao):
        f_matiere()
        assert dao.addActivite("1") == [
            {"id": 1, "matiere": 1, "nom": "nouvelle", "position": 0, "nbPages": 0},
        ]

    def test_updateActiviteNom(self, dao):
        f_activite(nom="bla")
        dao.updateActiviteNom(1, "meuh")
        with db_session:
            assert Activite[1].nom == "meuh"

    def test_getMatieres(self, dao):
        b_matiere(3, nom="rien", bgColor="red", fgColor="blue")
        f_activite(matiere=1)
        b_page(5, activite=1)
        assert dao.getMatieres(1) == [
            {
                "activites": [1],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": 1,
                "id": 1,
                "nom": "rien",
                "position": 0,
                "nbPages": 5,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": 1,
                "id": 2,
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": 1,
                "id": 3,
                "nom": "rien",
                "position": 2,
                "nbPages": 0,
            },
        ]

    def test_moveMatiere(self, dao):
        b_matiere(3, nom="rien", bgColor="red", fgColor="blue")
        assert dao.moveMatiereTo(3, 1) == [
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": 1,
                "id": 1,
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": 1,
                "id": 3,
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": 1,
                "id": 2,
                "nom": "rien",
                "position": 2,
                "nbPages": 0,
            },
        ]

    def test_removeMatieres(self, dao):
        b_matiere(3, nom="rien", bgColor="red", fgColor="blue")
        assert dao.removeMatiere(2) == [
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": 1,
                "id": 1,
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": 1,
                "id": 3,
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
        ]

    def test_addMatiere_by_matiereid(self, dao):
        b_matiere(3, nom="rien", bgColor="red", fgColor="blue")
        assert dao.addMatiere(2) == [
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": 1,
                "id": 1,
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("white"),
                "fgColor": QColor("black"),
                "groupe": 1,
                "id": 4,
                "nom": "nouvelle",
                "position": 1,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": 1,
                "id": 2,
                "nom": "rien",
                "position": 2,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": 1,
                "id": 3,
                "nom": "rien",
                "position": 3,
                "nbPages": 0,
            },
        ]

    def test_addMatiere_by_groupeid(self, dao):
        f_groupeMatiere()
        assert dao.addMatiere("1") == [
            {
                "activites": [],
                "bgColor": QColor.fromRgbF(1.000000, 1.000000, 1.000000, 1.000000),
                "fgColor": QColor.fromRgbF(0.000000, 0.000000, 0.000000, 1.000000),
                "groupe": 1,
                "id": 1,
                "nbPages": 0,
                "nom": "nouvelle",
                "position": 0,
            }
        ]

    def test_updateActiviteNom(self, dao):
        f_matiere(nom="bla")
        dao.updateMatiereNom(1, "meuh")
        with db_session:
            assert Matiere[1].nom == "meuh"

    def test_getGroupeMatieres(self, dao):
        b_groupeMatiere(3, annee=2017, nom="rien", bgColor="red", fgColor="blue")
        f_matiere(groupe=3)
        f_activite(matiere=1)
        b_page(2, activite=1)
        assert dao.getGroupeMatieres(2017) == [
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": 1,
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": 2,
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": 3,
                "nom": "rien",
                "position": 2,
                "nbPages": 2,
            },
        ]

    def test_removeGroupeMatiere(self, dao):
        b_groupeMatiere(3, annee=2017, nom="rien", bgColor="red", fgColor="blue")
        assert dao.removeGroupeMatiere(2) == [
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": 1,
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": 3,
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
        ]

    def test_moveGroupeMatiere(self, dao):
        b_groupeMatiere(3, annee=2017, nom="rien", bgColor="red", fgColor="blue")
        assert dao.moveGroupeMatiereTo(3, 1) == [
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": 1,
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": 3,
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": 2,
                "nom": "rien",
                "position": 2,
                "nbPages": 0,
            },
        ]

    def test_addGroupeMatieres(self, dao):
        b_groupeMatiere(3, annee=2017, nom="rien", bgColor="red", fgColor="blue")
        assert dao.addGroupeMatiere(3) == [
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": 1,
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": 2,
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("white"),
                "fgColor": QColor("black"),
                "id": 4,
                "nom": "nouveau",
                "position": 2,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": 3,
                "nom": "rien",
                "position": 3,
                "nbPages": 0,
            },
        ]
        with db_session:
            assert GroupeMatiere[4].matieres.select().first().nom == "nouvelle matière"

    @pytest.mark.parametrize(
        "nb, res, end_color",
        [
            (0, [], QColor("pink")),
            (
                1,
                [
                    {
                        "activites": [],
                        "bgColor": QColor.fromRgbF(
                            1.000000, 0.000000, 0.000000, 1.000000
                        ),
                        "fgColor": QColor.fromRgbF(
                            0.000000, 0.501961, 0.000000, 1.000000
                        ),
                        "groupe": 1,
                        "id": 1,
                        "nom": "rien",
                        "position": 0,
                        "nbPages": 0,
                    },
                ],
                QColor("red"),
            ),
            (
                3,
                [
                    {
                        "activites": [],
                        "bgColor": QColor.fromRgbF(
                            1.000000, 0.000000, 0.000000, 1.000000
                        ),
                        "fgColor": QColor.fromRgbF(
                            0.000000, 0.501961, 0.000000, 1.000000
                        ),
                        "groupe": 1,
                        "id": 1,
                        "nom": "rien",
                        "position": 0,
                        "nbPages": 0,
                    },
                    {
                        "activites": [],
                        "bgColor": QColor.fromRgbF(
                            1.000000, 0.423529, 0.423529, 1.000000
                        ),
                        "fgColor": QColor.fromRgbF(
                            0.000000, 0.501961, 0.000000, 1.000000
                        ),
                        "groupe": 1,
                        "id": 2,
                        "nom": "rien",
                        "position": 1,
                        "nbPages": 0,
                    },
                    {
                        "activites": [],
                        "bgColor": QColor.fromRgbF(
                            1.000000, 0.847059, 0.847059, 1.000000
                        ),
                        "fgColor": QColor.fromRgbF(
                            0.000000, 0.501961, 0.000000, 1.000000
                        ),
                        "groupe": 1,
                        "id": 3,
                        "nom": "rien",
                        "position": 2,
                        "nbPages": 0,
                    },
                ],
                QColor("red"),
            ),
        ],
    )
    def test_applyGroupeDegrade_with_color(self, dao, nb, res, end_color):
        f_groupeMatiere(bgColor="pink")
        b_matiere(nb, groupe=1, nom="rien", bgColor="blue", fgColor="green")
        assert dao.applyGroupeDegrade(1, QColor("red")) == res

        with db_session:
            assert GroupeMatiere[1].bgColor == end_color

    def test_reApplyGroupeDegrade(self, dao):
        f_groupeMatiere(bgColor="red")
        b_matiere(3, groupe=1, nom="rien", bgColor="blue", fgColor="green")
        assert dao.reApplyGroupeDegrade(1) == [
            {
                "activites": [],
                "bgColor": QColor.fromRgbF(1.000000, 0.000000, 0.000000, 1.000000),
                "fgColor": QColor.fromRgbF(0.000000, 0.501961, 0.000000, 1.000000),
                "groupe": 1,
                "id": 1,
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor.fromRgbF(1.000000, 0.423529, 0.423529, 1.000000),
                "fgColor": QColor.fromRgbF(0.000000, 0.501961, 0.000000, 1.000000),
                "groupe": 1,
                "id": 2,
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor.fromRgbF(1.000000, 0.847059, 0.847059, 1.000000),
                "fgColor": QColor.fromRgbF(0.000000, 0.501961, 0.000000, 1.000000),
                "groupe": 1,
                "id": 3,
                "nom": "rien",
                "position": 2,
                "nbPages": 0,
            },
        ]

        with db_session:
            assert GroupeMatiere[1].bgColor == QColor("red")

    def test_updateGroupeNom(self, dao):
        f_groupeMatiere(nom="bla")
        dao.updateGroupeMatiereNom(1, "meuh")
        with db_session:
            assert GroupeMatiere[1].nom == "meuh"


class TestDatabaseObject:
    # def test_init_settings(self, ddbr, dao):
    #     # settings pas inité en mode debug (default
    #     assert DatabaseObject(ddbr).annee_active is None
    #
    #     # settings inités en non debug
    #     with patch.object(DatabaseObject, "setup_settings") as m:
    #         DatabaseObject(ddbr, debug=False)
    #         assert m.call_args_list == [call()]
    #
    #     # init matiere dsi annee_active
    #     class DBO(DatabaseObject):
    #         anne_active = 1983
    #
    #     x = DBO(ddbr, debug=False)

    def test_initialize_session(self, dao):
        assert dao.annee_active == 2019
        assert dao.currentUser == {
            "id": 1,
            "last_used": 0,
            "nom": "lenom",
            "prenom": "leprenom",
        }

    def test_files(self, dao):
        assert dao.files == FILES

    def test_RecentsItem_Clicked(self, ddbr, qtbot):
        rec1 = f_page(created=datetime.now(), td=True)
        d = DatabaseObject(ddbr)
        d.recentsItemClicked.emit(rec1["id"], rec1["matiere"])
        assert d.currentMatiere == rec1["matiere"]
        assert d.currentPage == rec1["id"]

    def test_onNewPageCreated(self, ddbr, qtbot):
        a = f_page(td=True)
        d = DatabaseObject(ddbr)
        d.onNewPageCreated(a)
        assert d.currentPage == a["id"]
        assert d.currentMatiere == a["matiere"]

    def test_onCurrentTitreSetted(self, ddbr, qtbot):
        a = f_page(td=True)
        d = DatabaseObject(ddbr)
        with qtbot.wait_signals(
            [
                (d.pagesParSectionChanged, "activites"),
                (d.recentsModelChanged, "recentchanged"),
            ]
        ):
            d.currentTitreSetted.emit()

    def test_onSectionAdded(self, dao, ddbn, qtbot):
        p = f_page()
        s1 = f_section(page=p.id)
        s2 = f_section(page=p.id)
        dao.pageModel.slotReset(p.id)
        assert s1.position == 0
        assert s2.position == 1
        newid = dao.addSection(p.id, {"classtype": "TextSection"})
        with db_session:
            item = ddbn.Section[newid]
            flush()
            assert item.position == 2
        p = dao.pageModel
        assert p.rowCount() == 3
        assert p.data(p.index(2, 0), p.PageRole)["id"] == str(item.id)

    def test_currentPageChanged(self, dao, ddbr, qtbot):
        a = f_page(td=True)
        with qtbot.wait_signals(
            [
                (dao.pageModel.modelReset, "model"),
                (dao.currentMatiereChanged, "matiere"),
                (dao.pagesParSectionChanged, "activite"),
            ],
            # timeout=2000,
        ):
            dao.currentPage = 1
        assert dao.currentMatiere == a["matiere"]

    def test_currentPageChanged_With_ZERO(self, dao, ddbr, qtbot):
        a = f_page(td=True)
        dao.currentPage = 1

        with qtbot.waitSignal(dao.updateRecentsAndActivites):
            dao.currentPage = 0

        assert dao.pageModel.page == None
        assert dao.currentMatiere == a["matiere"]

    def test_updateRecentsAndActivites(self, dao, qtbot):
        with qtbot.waitSignals([dao.recentsModelChanged, dao.pagesParSectionChanged]):
            dao.updateRecentsAndActivites.emit()

    def test_currentMaterieResed(self, dao):
        m = f_matiere()
        a = f_page()
        dao.currentPage = 1
        dao.matiereReset.emit()
        assert dao.currentPage == 0

    def test_changeAnnee(self, dao, qtbot):
        # setup
        assert dao.annee_active == 2019
        f_annee(2020)
        g = f_groupeMatiere(annee=2019)
        m = f_matiere(groupe=g.id)
        ac = f_activite(matiere=m)
        p = f_page(activite=ac.id, created=datetime.now())
        dao.currentPage = 1
        assert dao.currentMatiere == m.id
        assert len(dao.recentsModel) == 1

        # test
        with qtbot.waitSignal(dao.anneeActiveChanged):
            dao.changeAnnee.emit(2020)
            assert dao.annee_active == 2020
            assert dao.currentPage == 0
            assert dao.currentMatiere == 0
            assert dao.m_d.annee.id == 2020
            assert len(dao.recentsModel) == 0
            assert len(dao.matieresList) == 0

    def test_image_update_update_recents_and_activite(self, dao, qtbot):
        with qtbot.waitSignal(dao.updateRecentsAndActivites):
            dao.imageChanged.emit()

    def test_equation_update_update_recents_and_activite(self, dao, qtbot):
        with qtbot.waitSignal(dao.updateRecentsAndActivites):
            dao.equationChanged.emit()

    def test_page_activite_changed_update_pagesParsection(self, dao, qtbot):
        with qtbot.waitSignal(dao.pagesParSectionChanged):
            dao.pageActiviteChanged.emit()
