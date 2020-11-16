import json
import shutil
import uuid
from datetime import datetime
from time import sleep

import pytest
from PIL import Image
from PySide2.QtCore import QUrl, Qt, QPointF
from PySide2.QtGui import QColor, QImage, QCursor
from PySide2.QtQuick import QQuickItem
from package.cursors import build_one_image_cursor
from fixtures import check_args
from package import constantes
from package.database_mixins.image_section_mixin import ImageSectionMixin
from package.database_mixins.matiere_mixin import MatieresDispatcher
from package.database_object import DatabaseObject
from unittest.mock import patch, call

from package.default_matiere import MATIERE_GROUPE, MATIERES
from package.files_path import FILES
from package.operations.api import create_operation
from package.page import text_section
from pony.orm import ObjectNotFound, db_session


class TestPageMixin:
    def test_check_args(self, dao: DatabaseObject):
        check_args(dao.newPage, str, dict)
        check_args(dao.removePage, str)
        check_args(dao.setCurrentTitre, str)
        check_args(dao.exportToPDF)
        check_args(dao.exportToOdt)

    def test_init(self, dao):
        assert dao._currentPage == ""
        assert dao._currentTitre == ""
        assert dao._currentEntry == None

        assert dao.timer_titre.isSingleShot()

    def test_newPage(self, fk, dao, qtbot, qappdao):
        f = fk.f_page()  # pour avoir plusieurs dans le resultats
        with qtbot.wait_signal(dao.newPageCreated, timeout=100):
            r = dao.newPage(f.activite.id)

    def test_currentPage(self, fk, dao, qtbot):
        a = fk.f_page()
        b = fk.f_page()
        assert dao.currentPage == ""

        # setCurrentPage with UUID
        dao.currentPage = a.id
        assert dao.currentPage == str(a.id)

        # Set CurrentPage with str
        with qtbot.wait_signal(dao.currentPageChanged, timeout=100):
            dao.currentPage = str(b.id)
        assert dao.currentPage == str(b.id)

        # set currentpage do nothing if same id
        with qtbot.assertNotEmitted(dao.currentPageChanged):
            dao.currentPage = b.id
        assert dao.currentPage == str(b.id)

        # set currentpage do nothing if same id
        with qtbot.assertNotEmitted(dao.currentPageChanged):
            dao.currentPage = b.id
        assert dao.currentPage == str(b.id)

    def test_current_entry(self, dao, fk):
        a = fk.f_page()
        dao.currentPage = a.id
        with db_session:
            assert (
                dao._currentEntry.titre
                == a.titre
                == dao._currentTitre
                == dao.currentTitre
            )

    def test_CurrentTitreSet(self, fk, dao):
        a = fk.b_page(2)

        # case no current page
        dao.currentTitre = "omk"
        assert dao._currentTitre == ""
        dao.currentPage = a[0].id
        with patch.object(dao.timer_titre, "start") as m:
            dao.currentTitre = "mokmk"
            assert dao.currentTitre == "mokmk"
            assert m.call_args_list == [call(500)]

            # do not call storage if same value
            dao.currentTitre = "mokmk"
            assert m.call_args_list == [call(500)]

    def test_UnderscoreCurrentTitreSet(self, fk, dao, qtbot):
        a = fk.f_page()
        dao.currentPage = a.id
        dao.TITRE_TIMER_DELAY = 0
        with qtbot.wait_signal(dao.currentTitreChanged):
            dao.currentTitre = "aaa"
        with db_session:
            assert dao.db.Page[a.id].titre == "aaa"

    def test_setCurrentTitre(self, dao, qtbot, fk):
        a = fk.f_page()
        dao.currentPage = a.id
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

    def test_on_pagechanged_reset_model(self, dao, fk):
        p1 = fk.f_page()
        fk.f_section(page=p1.id)
        dao.currentPage = p1.id
        with db_session:
            assert dao.pageModel.page.id == p1.id

    def test_removePAge(self, dao, qtbot, fk):
        a = fk.f_page()
        dao.removePage(a.id)
        with db_session:
            assert not dao.db.Page.get(id=1)
        assert dao.currentPage == ""

    def test_removePAge_no_item_in_db(self, dao, qtbot):
        dao.removePage(99)
        assert dao.currentPage == ""

    def test_removePAge_blanck_if_currentItem(self, dao, fk):
        a = fk.f_page()
        dao.currentPage = a.id
        dao.removePage(a.id)
        assert dao.currentPage == ""

    def test_allow_currentPAge_can_be_empty(self, dao, fk):
        a = fk.f_page()
        dao.currentPage = a.id
        dao.currentPage = ""

    def test_export_to_pdf(selfsekf, dao, fk):
        a = fk.f_page(titre="blà")
        dao.currentPage = a.id
        with patch("package.database_mixins.page_mixin.QDesktopServices.openUrl") as m:
            with patch("package.database_mixins.page_mixin.soffice_convert") as v:
                dao._export_to_pdf()
                v.assert_called_with(
                    str(a.id), "pdf:writer_pdf_Export", "bla.pdf", dao.ui
                )
                m.assert_called_with(v.return_value.as_uri())

    def test_exportToPDf(self, dao, qtbot):
        with patch.object(dao, "_export_to_pdf") as w:
            with qtbot.waitSignal(
                dao.ui.sendToast,
                check_params_cb=lambda x: x
                == "Export en PDF lancé, cela peut prendre plusieurs secondes",
            ):
                dao.exportToPDF()
            sleep(1 / 1000)

        assert w.called

    def test_export_to_odt(selfsekf, dao, fk):
        a = fk.f_page(titre="blà")
        dao.currentPage = a.id
        with patch("package.database_mixins.page_mixin.QDesktopServices.openUrl") as m:
            with patch("package.database_mixins.page_mixin.soffice_convert") as v:
                dao._export_to_odt()
                v.assert_called_with(str(a.id), "odt", "bla.odt", dao.ui)
                m.assert_called_with(v.return_value.as_uri())

    def test_exportToOdt(self, dao, qtbot):
        with patch.object(dao, "_export_to_odt") as w:
            with qtbot.waitSignal(
                dao.ui.sendToast,
                check_params_cb=lambda x: x
                == "Export en ODT lancé, cela peut prendre plusieurs secondes",
            ):

                dao.exportToOdt()
            sleep(1 / 1000)
        assert w.called


@pytest.fixture()
def create_matiere(
    fk,
):
    gp = fk.f_groupeMatiere(annee=2019)

    def activ(mat):
        return (
            fk.f_activite(nom="un", matiere=mat),
            fk.f_activite(nom="deux", matiere=mat),
            fk.f_activite(nom="trois", matiere=mat),
        )

    _mats = []
    a = fk.f_matiere("un", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id)
    _mats.append(str(a.id))
    a = fk.f_matiere("deux", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id)
    _mats.append(str(a.id))
    a = fk.f_matiere("trois", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id)
    _mats.append(str(a.id))
    a = fk.f_matiere("quatre", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id)
    _mats.append(str(a.id))
    gp._mats = _mats
    gp._acts = []
    for m in gp._mats:
        gp._acts.append(activ(m))
    return gp


class TestMatiereMixin:
    def test_check_args(self, dao: DatabaseObject):
        check_args(dao.getMatiereIndexFromId, str, int)
        check_args(dao.matieresListRefresh)

    def test_init(self, dao):
        assert dao._currentMatiere == ""

    def test_currentMatiere(self, dao, qtbot, create_matiere):
        assert dao.currentMatiere == ""
        dao.init_matieres()

        # from int
        with db_session:
            mats = [x for x in dao.db.Matiere.select()]
        mat2 = mats[1]
        with qtbot.waitSignal(dao.currentMatiereChanged, timeout=100):
            dao.currentMatiere = mat2.id

        assert dao.currentMatiere == str(mat2.id)
        dao.currentMatiere = "fez"  # not in do nothing
        assert dao.currentMatiere == ""

        # from index
        with qtbot.waitSignal(dao.matiereReset):
            dao.setCurrentMatiereFromIndex(2)
        assert dao.currentMatiere == str(mats[2].id)

        # get index from id
        assert dao.getMatiereIndexFromId(str(mats[2].id)) == 2
        assert dao.getMatiereIndexFromId("99999") is 0

    def test_currentMatiereItem(self, fk, dao):
        m = fk.f_matiere(td=True)
        dao.currentMatiere = m["id"]
        assert dao.currentMatiereItem == m

    def test_matiereList(
        self,
        dao,
        create_matiere,
        fk,
    ):
        dao.init_matieres()
        x = create_matiere
        # listnom
        reslist = [
            {
                "activites": [
                    str(x._acts[0][0].id),
                    str(x._acts[0][1].id),
                    str(x._acts[0][2].id),
                ],
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "id": x._mats[0],
                "groupe": str(x.id),
                "nom": "un",
                "position": 0,
            },
            {
                "activites": [
                    str(x._acts[1][0].id),
                    str(x._acts[1][1].id),
                    str(x._acts[1][2].id),
                ],
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": str(x.id),
                "id": x._mats[1],
                "nom": "deux",
                "position": 1,
            },
            {
                "activites": [
                    str(x._acts[2][0].id),
                    str(x._acts[2][1].id),
                    str(x._acts[2][2].id),
                ],
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": str(x.id),
                "id": x._mats[2],
                "nom": "trois",
                "position": 2,
            },
            {
                "activites": [
                    str(x._acts[3][0].id),
                    str(x._acts[3][1].id),
                    str(x._acts[3][2].id),
                ],
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": str(x.id),
                "id": x._mats[3],
                "nom": "quatre",
                "position": 3,
            },
        ]
        assert dao.matieresList == reslist

        # refresh
        cinq = fk.f_matiere(
            "cinq",
            groupe=fk.f_groupeMatiere(annee=2019),
            _fgColor=4294967295,
            _bgColor=4294901760,
        )
        c1 = fk.f_activite(matiere=cinq.id)
        c2 = fk.f_activite(matiere=cinq.id)
        c3 = fk.f_activite(matiere=cinq.id)
        dao.matieresListRefresh()
        reslist.append(
            {
                "activites": [str(c1.id), str(c2.id), str(c3.id)],
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": str(cinq.groupe.id),
                "id": str(cinq.id),
                "nom": "cinq",
                "position": 0,
            }
        )
        assert dao.matieresList == reslist

    def test_pagesParSection(self, fk, dao):
        assert dao.pagesParSection == []
        acts = fk.b_activite(3)
        p = fk.f_page(td=True, activite=str(acts[2].id))
        dao.currentMatiere = p["matiere"]
        assert dao.pagesParSection[0]["id"] == str(acts[0].id)
        assert dao.pagesParSection[1]["id"] == str(acts[1].id)
        assert dao.pagesParSection[2]["id"] == str(acts[2].id)
        assert dao.pagesParSection[2]["pages"] == [p]

    def test_matiere_dispatch(self, fk):
        # anne n'exist pas
        with pytest.raises(ObjectNotFound):
            MatieresDispatcher(fk.db, 2000)
        # assert m.annee.id == 2000

        # anne existe
        fk.f_annee(1954)
        m = MatieresDispatcher(fk.db, 1954)
        assert m.annee.id == 1954


class TestActiviteMixin:
    def test_check_args(self, dao):
        check_args(dao.getDeplacePageModel, int, list)
        check_args(dao.changeActivite, [str, str])

    def test_getDeplacePageModel(self, fk, dao):
        g1 = fk.f_groupeMatiere(annee=1900)
        g2 = fk.f_groupeMatiere(annee=2000)
        m1 = fk.f_matiere(nom="un", groupe=g1)
        m2 = fk.f_matiere(nom="deux", groupe=g1)
        m3 = fk.f_matiere(nom="trois", groupe=g2, bgColor="red")
        m4 = fk.f_matiere(nom="quatre", groupe=g2, bgColor="blue")
        acs = []
        for i in [m1, m2, m3, m4]:
            acs = acs + [*fk.b_activite(3, nom="rien", matiere=i.id)]
        res = dao.getDeplacePageModel(2000)
        assert res == [
            {
                "activites": [
                    {"id": str(acs[6].id), "nom": "rien"},
                    {"id": str(acs[7].id), "nom": "rien"},
                    {"id": str(acs[8].id), "nom": "rien"},
                ],
                "bgColor": QColor("red"),
                "nom": "trois",
            },
            {
                "activites": [
                    {"id": str(acs[9].id), "nom": "rien"},
                    {"id": str(acs[10].id), "nom": "rien"},
                    {"id": str(acs[11].id), "nom": "rien"},
                ],
                "bgColor": QColor("blue"),
                "nom": "quatre",
            },
        ]

    def test_changeActivite(self, fk, dao, qtbot):
        s = fk.f_activite()
        a = fk.f_page()
        with db_session:
            actt = a.activite.id
            assert dao.db.Page[a.id].activite.id == actt
        with qtbot.waitSignal(dao.pageActiviteChanged):
            dao.changeActivite(a.id, s.id)
        with db_session:
            assert dao.db.Page[a.id].activite.id == s.id


class TestRecentsMixin:
    def test_init(self, fk, dao, ddbn):
        a = fk.b_page(5)
        with db_session:
            ddbn.Page.recents == dao.recentsModel


class TestLayoutMixin:
    def test_check_args(self, dao):
        check_args(dao.getLayoutSizes, str, float)
        check_args(dao.setStyle, (str, dict), dict)

    def test_getlayoutsize(self, dao: DatabaseObject):
        assert (
            dao.getLayoutSizes("preferredCentralWidth")
            == constantes.preferredCentralWidth
        )

    def test_setStyle(self, fk, dao: DatabaseObject, caplogger):
        a = fk.f_style()

        # normal
        r = dao.setStyle(a.styleId, {"underline": True, "bgColor": "red"})
        assert r == {
            "bgColor": QColor("red"),
            "family": "",
            "fgColor": QColor("black"),
            "styleId": str(a.styleId),
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
        # breakpoint()
        assert "Unknown attribute 'badparam'" in caplogger.records[0][2]
        assert caplogger.records[0][1].replace(" ", "") == "ERROR"
        caplogger.truncate(0)

        # style does not exists
        with db_session:
            b = dao.db.Style[a.styleId]
            b.delete()

        r = dao.setStyle(a.styleId, {"underline": True})
        assert (
            caplogger.records[0][2][52:]  # Horrible  à refaire avec caplogger
            == f"Echec de la mise à jour du style : ObjectNotFound  Style[{repr(a.styleId)}]"
        )
        assert caplogger.records[0][1].replace(" ", "") == "ERROR"

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

    def test_loadsection_image(self, fk, dao):
        s = fk.f_imageSection(path="bla/ble.jpg")
        res = dao.loadSection(s.id)
        assert res["id"] == str(s.id)
        assert res["path"] == QUrl.fromLocalFile(str(FILES / "bla/ble.jpg"))

    def test_loadsection_image_false(self, dao):
        res = dao.loadSection(99999)
        assert res == {}

    def test_load_section_Operation(self, fk, dao):
        a = fk.f_additionSection(string="3+4")
        assert dao.loadSection(a.id) == {
            "classtype": "AdditionSection",
            "created": a.created.isoformat(),
            "datas": ["", "", "", "3", "+", "4", "", ""],
            "rows": 4,
            "columns": 2,
            "id": str(a.id),
            "modified": a.modified.isoformat(),
            "page": str(a.page.id),
            "position": 0,
            "size": 8,
            "virgule": 0,
        }

    def test_load_section_tableau(self, fk, dao):
        a = fk.f_tableauSection(lignes=3, colonnes=3)
        assert dao.loadSection(a.id) == {
            "classtype": "TableauSection",
            "created": a.created.isoformat(),
            "colonnes": 3,
            "id": str(a.id),
            "lignes": 3,
            "modified": a.modified.isoformat(),
            "page": str(a.page.id),
            "position": 0,
        }

    def test_loadsection_equation(self, fk, dao):
        eq = fk.f_equationSection(content="1+2", td=True)
        with db_session:
            pageid = str(dao.db.EquationSection[eq["id"]].page.id)
        assert dao.loadSection(eq["id"]) == {
            "classtype": "EquationSection",
            "created": eq["created"],  # .created.isoformat(),
            "content": "1+2",
            "id": eq["id"],
            "modified": eq["modified"],  # a.modified.isoformat(),
            "page": pageid,
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
            (1, {"classtype": "ImageSectionVide", "width": 10, "height": 20}, 1, True),
        ],
    )
    def test_addSection(self, fk, dao, ddbn, qtbot, page, content, res, signal_emitted):
        x = fk.f_page()
        page = x.id
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
            (
                1,
                {
                    "path": "png_annot",
                    "classtype": "ImageSection",
                },
                1,
                True,
            ),
            (
                1,
                {
                    "path": QUrl("no/existe"),
                    "classtype": "ImageSection",
                },
                0,
                False,
            ),
            (
                1,
                {
                    "path": "createOne",
                    "classtype": "ImageSection",
                },
                1,
                True,
            ),
            (
                1,
                {
                    "path": QUrl("createOne"),
                    "classtype": "ImageSection",
                },
                1,
                True,
            ),
            (
                1,
                {
                    "path": None,
                    "classtype": "ImageSection",
                },
                0,
                False,
            ),
            (1, {"path": "my/path", "classtype": "ImageSection"}, 0, False),
        ],
    )
    def test_addSectionFile(
        self,
        png_annot,
        resources,
        daof,
        fkf,
        qtbot,
        page,
        content,
        res,
        signal_emitted,
        tmpfile,
        qappdaof,
    ):

        x = fkf.f_page()
        page = x.id
        print("dans test", fkf.db, daof.db)
        daof.pageModel.slotReset(x.id)
        if "path" not in content:
            pass
        if content["path"] == "png_annot":
            content["path"] = str(png_annot)
        elif isinstance(content["path"], QUrl):
            if content["path"].toString() == "createOne":
                content["path"] = QUrl.fromLocalFile(str(tmpfile))
        elif content["path"] == "createOne":
            content["path"] = str(tmpfile)
        if signal_emitted:
            with qtbot.waitSignal(daof.sectionAdded):
                a = daof.addSection(page, content)
        else:
            a = daof.addSection(page, content)

        with db_session:
            if res:
                _res = str(
                    fkf.db.Section.select().order_by(lambda x: x.position).first().id
                )
                res = _res
            else:
                res = ""
        assert a == res
        if res == "":
            return
        with db_session:
            item = fkf.db.Section.select().first()
            assert item.page.id == x.id
            for i in content.keys():
                if i == "path":
                    assert content[i] == getattr(item, i)
                    assert (FILES / item.path).exists()
                elif i == "string":
                    item.datas == create_operation(content["string"])
                else:
                    assert content[i] == getattr(item, i)

    def test_addSetion_create_empty_image(self, fk, dao, qtbot, qappdao):
        page = fk.f_page().id
        dao.pageModel.slotReset(page)
        content = {"classtype": "ImageSectionVide", "height": 20, "width": 10}
        with qtbot.waitSignal(dao.sectionAdded):
            res = dao.addSection(str(page), content)

    def test_addSection_pdf(self, fkf, daof, resources, qtbot, qappdaof):
        page = fkf.f_page().id
        daof.pageModel.slotReset(page)
        content = {"classtype": "ImageSection"}
        content["path"] = str(resources / "2pages.pdf")
        with qtbot.waitSignal(daof.sectionAdded, timeout=5000):
            res = daof.addSection(str(page), content)
        with db_session:
            item = fkf.db.Page[page].sections.count() == 2


class TestEquationMixin:
    def test_check_args(self, dao):
        check_args(dao.updateEquation, [str, str, int, str], dict)
        check_args(dao.isEquationFocusable, [str, int], bool)

    def test_update(self, dao, fk, qtbot):
        e = fk.f_equationSection(content=" \n1\n ")
        event = json.dumps({"key": int(Qt.Key_2), "text": "2", "modifiers": None})
        with qtbot.waitSignal(dao.equationChanged):
            res = dao.updateEquation(e.id, " \n1\n ", 3, event)
        assert res == {"content": "  \n12\n  ", "curseur": 5}

    def test_isequationfocusable(self, dao):
        assert not dao.isEquationFocusable("  \n1 \n  ", 0)
        assert dao.isEquationFocusable("  \n1 \n  ", 4)


class TestImageSectionMixin:
    def test_check_args(self, dao: ImageSectionMixin):
        check_args(dao.pivoterImage, [str, int], bool)

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

    def test_create_empty_image(
        self,
        dao,
    ):
        res = dao.create_empty_image(300, 500)
        im = Image.new("RGBA", (300, 500), "white")
        saved = Image.open(dao.files / res)
        assert list(im.getdata()) == list(saved.getdata())

    def test_pivoter_image(self, new_res, fk, dao, qtbot):
        file = new_res("test_pivoter.png")
        img = Image.open(file)
        assert img.height == 124
        assert img.width == 673

        f = fk.f_imageSection(path=str(file))
        with qtbot.waitSignal(dao.imageChanged):
            dao.pivoterImage(f.id, 1)
        img = Image.open(file)
        assert img.height == 673
        assert img.width == 124

    trait_600_600 = "data:image/png;base64,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"
    trait_600_600_as_png = "2019/2019-05-21-12-00-01-349bd.png"

    def test_annotationTextBGOpacity(self, dao):
        assert dao.annotationTextBGOpacity == 0.5

    @pytest.mark.parametrize(
        "pos, img_res",
        [
            (QPointF(0.10, 0.10), "floodfill_blanc_en_bleu.png"),
            (QPointF(0.80, 0.80), "floodfill_rouge_en_bleu.png"),
        ],
    )
    def test_flood_fill(self, fk, dao, resources, tmp_path, pos, img_res):
        fp = tmp_path / "f1.png"
        shutil.copy(resources / "floodfill.png", fp)
        f = fk.f_imageSection(path=str(fp))
        assert dao.floodFill(f.id, QColor("blue"), pos)
        assert QImage(str(dao.files / f.path)) == QImage(str(resources / img_res))

    def test_image_selection_curosr(self, dao, qtbot):
        qk = QQuickItem()

        # defaut
        dao.setImageSectionCursor(qk)
        assert (
            qk.cursor().pixmap().toImage()
            == build_one_image_cursor("text").pixmap().toImage()
        )
        # color
        dao.ui.annotationDessinCurrentStrokeStyle = QColor("blue")
        dao.setImageSectionCursor(
            qk,
        )
        # qk.cursor().pixmap().toImage().save("/tmp/aa1.png")
        # build_one_image_cursor("text", QColor("blue")).pixmap().toImage().save(
        #     "/tmp/aa2.png"
        # )
        assert (
            qk.cursor().pixmap().toImage()
            == build_one_image_cursor("text", QColor("blue")).pixmap().toImage()
        )

        # with tool
        dao.ui.annotationDessinCurrentStrokeStyle = QColor("red")
        dao.setImageSectionCursor(qk, "fillrect")
        assert (
            qk.cursor().pixmap().toImage()
            == build_one_image_cursor("fillrect", QColor("red")).pixmap().toImage()
        )

        # default
        dao.setImageSectionCursor(qk, "default")
        assert qk.cursor() == QCursor(Qt.ArrowCursor)

        # dragmove
        dao.setImageSectionCursor(qk, "dragmove")
        assert qk.cursor() == QCursor(Qt.DragMoveCursor)


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

    def test_init_datas(self, dao, fk):
        x = fk.f_tableauSection(3, 4)

        with db_session:
            assert dao.initTableauDatas(str(x.id)) == [
                x.to_dict() for x in dao.db.TableauSection[x.id].get_cells()
            ]

    def test_updat_cell(self, dao, qtbot, fk):
        x = fk.f_tableauCell(x=2, y=3, texte="zer")

        with qtbot.waitSignal(dao.tableauChanged):
            dao.updateCell(x.tableau.id, 3, 2, {"texte": "bla"})
        with db_session:
            assert dao.db.TableauCell[x.tableau.id, 3, 2].texte == "bla"

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
    def test_add_remove_row_column(self, fk, dao, qtbot, fn, lignes, colonnes):
        x = fk.f_tableauSection(2, 2)
        with qtbot.waitSignal(dao.tableauLayoutChanged):
            getattr(dao, fn)(x.id, 1)
        with db_session:
            x = dao.db.TableauSection[x.id]
            assert x.lignes == lignes
            assert x.colonnes == colonnes

    @pytest.mark.parametrize(
        "fn, lignes, colonnes",
        [
            ("appendColumn", 2, 3),
            ("appendRow", 3, 2),
        ],
    )
    def test_append_row_column(self, fk, dao, qtbot, fn, lignes, colonnes):
        x = fk.f_tableauSection(2, 2)
        with qtbot.waitSignal(dao.tableauLayoutChanged):
            getattr(dao, fn)(x.id)
        with db_session:
            x = dao.db.TableauSection[x.id]
            assert x.lignes == lignes
            assert x.colonnes == colonnes

    def test_nb_colonnes(self, fk, dao):
        x = fk.f_tableauSection(2, 6)
        assert dao.nbColonnes(x.id) == 6


class TestTextSectionMixin:
    def test_check_args(self, dao):
        check_args(dao.updateTextSectionOnKey, [str, str, int, int, int, str], dict)
        check_args(dao.updateTextSectionOnChange, [str, str, int, int, int], dict)
        check_args(dao.updateTextSectionOnMenu, [str, str, int, int, int, dict], dict)
        check_args(dao.loadTextSection, str, dict)
        check_args(dao.getTextSectionColor, str, QColor)

    def test_updateTextSectionOnKey(self, fk, dao):
        fk.f_textSection(text="bla")
        dic_event = {"key": int(Qt.Key_B), "modifiers": int(Qt.ControlModifier)}
        event = json.dumps(dic_event)
        args = 1, "bla", 3, 3, 3

        with patch("package.database_mixins.text_mixin.TextSectionEditor") as m:
            res = dao.updateTextSectionOnKey(*args, event)
            m.assert_called_with(*args)
            m.return_value.onKey.assert_called_with(dic_event)
            assert res == m.return_value.onKey.return_value

    def test_updateTextSectionOnChange(self, fk, dao, qtbot):
        fk.f_textSection(text="bla")
        dic_event = {"key": int(Qt.Key_B), "modifiers": int(Qt.ControlModifier)}
        args = 1, "blap", 3, 3, 4

        with patch("package.database_mixins.text_mixin.TextSectionEditor") as m:
            with qtbot.waitSignal(dao.textSectionChanged):
                res = dao.updateTextSectionOnChange(*args)
            m.assert_called_with(*args)
            m.return_value.onChange.assert_called_with()
            assert res == m.return_value.onChange.return_value

    def test_updateTextSectionOnMenu(self, fk, dao):
        fk.f_textSection()
        dic_params = {"ble": "bla"}
        # params = json.dumps(dic_params)
        args = 1, "bla", 3, 3, 3

        with patch("package.database_mixins.text_mixin.TextSectionEditor") as m:
            res = dao.updateTextSectionOnMenu(*args, dic_params)
            m.assert_called_with(*args)
            m.return_value.onMenu.assert_called_with(ble="bla")
            assert res == m.return_value.onMenu.return_value

    def test_loadTextSection(self, fk, dao):
        fk.f_textSection()

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
    def test_check_args(self, dao):
        check_args(dao.newUser, [str, str])
        check_args(dao.newAnnee, [int, str])
        check_args(dao.getMenuAnnees, None, list)

    @db_session
    def test_init_user(self, dao, userid):
        with db_session:
            user = dao.db.Utilisateur.select().first()
        assert dao.init_user() == {
            "id": userid,
            "last_used": 2019,
            "nom": "nom",
            "prenom": "prenom",
        }
        dao.db.Utilisateur.user().delete()
        assert dao.init_user() == {}

    def test_newUser(self, dao, qtbot):

        # existe déja
        with pytest.raises(AssertionError):
            dao.newUser(nom="oj", prenom="omj")

        # n'existe pas
        with db_session:
            dao.db.Utilisateur.user().delete()

        with qtbot.waitSignal(dao.currentUserChanged):
            dao.newUser(nom="oj", prenom="omj")
        with db_session:
            user = dao.db.Utilisateur.select().first()
        assert dao.currentUser == {
            "id": str(user.id),
            "last_used": 0,
            "nom": "oj",
            "prenom": "omj",
        }
        assert dao.currentUser == dao.current_user

    def test_newAnnee(self, dao):
        dao.newAnnee(2050, "ce3")
        with db_session:
            an = dao.db.Annee[2050]
            assert an.niveau == "ce3"
            assert an.user == dao.db.Utilisateur.user()

    def test_getMenuesAnnees(self, fk, dao):
        with db_session:
            user = dao.db.Utilisateur.select().first()
        for i in range(4):
            fk.f_annee(2016 - (i * i), user=str(user.id))  # pour tester l'ordre
        assert dao.getMenuAnnees() == [
            {"id": 2007, "niveau": "cm2007", "user": str(user.id)},
            {"id": 2012, "niveau": "cm2012", "user": str(user.id)},
            {"id": 2015, "niveau": "cm2015", "user": str(user.id)},
            {"id": 2016, "niveau": "cm2016", "user": str(user.id)},
            {
                "id": 2019,
                "niveau": "cm2019",
                "user": str(user.id),
            },  # 2019 setté dans la fixture dao
        ]

    def test_anneActive(self, dao):
        assert dao.anneeActive == 2019

    def test_anneeactive_set_sans_user(self, dao, qtbot):
        with patch.object(dao.db.Utilisateur, "user", return_value=None):
            with qtbot.assertNotEmitted(dao.anneeActiveChanged):
                dao.anneeActive = 1234
        with db_session:
            assert dao.db.Utilisateur.user().last_used == 2019


class TestDatabaseObject:
    # def test_init_settings(self, fk, dao):
    #     # settings pas inité en mode debug (default
    #     assert DatabaseObject(ddbr).annee_active is None
    #
    #     # settings inités en non debug
    #     with patch.object(DatabaseObject, "setup_settings") as m:
    #         DatabaseObject(fk, debug=False)
    #         assert m.call_args_list == [call()]
    #
    #     # init matiere dsi annee_active
    #     class DBO(DatabaseObject):
    #         anne_active = 1983
    #
    #     x = DBO(fk, debug=False)

    def test_initialize_session(self, dao, userid):
        assert dao.annee_active == 2019
        assert dao.currentUser == {
            "id": userid,
            "last_used": 0,
            "nom": "nom",
            "prenom": "prenom",
        }

    def test_init_change_annee(self, fk, uim):

        a = DatabaseObject(fk.db, uim)
        assert a.anneeActive == None
        assert a.currentPage == ""
        assert a.currentMatiere == ""

    def test_files(self, dao):
        assert dao.files == FILES

    def test_RecentsItem_Clicked(self, fk, qappdao, uim):
        rec1 = fk.f_page(created=datetime.now(), td=True)
        d = qappdao.dao
        d.recentsItemClicked.emit(rec1["id"], rec1["matiere"])
        assert d.currentMatiere == rec1["matiere"]
        assert d.currentPage == rec1["id"]

    def test_onNewPageCreated(self, fk, qappdao, uim):
        a = fk.f_page(td=True)
        d = qappdao.dao
        d.onNewPageCreated(a)
        assert d.currentPage == a["id"]
        assert d.currentMatiere == a["matiere"]

    def test_onCurrentTitreSetted(self, fk, qappdao, qtbot, uim):
        a = fk.f_page(td=True)
        d = qappdao.dao
        with qtbot.wait_signals(
            [
                (d.pagesParSectionChanged, "activites"),
                (d.recentsModelChanged, "recentchanged"),
            ]
        ):
            d.currentTitreSetted.emit()

    def test_onSectionAdded(self, dao, fk, ddbn, qtbot):
        p = fk.f_page()
        s1 = fk.f_section(page=p.id)
        s2 = fk.f_section(page=p.id)
        dao.pageModel.slotReset(p.id)
        assert s1.position == 0
        assert s2.position == 1
        newid = dao.addSection(p.id, {"classtype": "TextSection"})
        with db_session:
            item = ddbn.Section[newid]
            item.flush()
            assert item.position == 2
        p = dao.pageModel
        assert p.rowCount() == 3
        assert p.data(p.index(2, 0), p.PageRole)["id"] == str(item.id)

    def test_currentPageChanged(self, dao, fk, qtbot):
        a = fk.f_page(td=True)
        with qtbot.wait_signals(
            [
                (dao.pageModel.modelReset, "model"),
                (dao.currentMatiereChanged, "matiere"),
                (dao.pagesParSectionChanged, "activite"),
            ],
            # timeout=2000,
        ):
            dao.currentPage = str(a["id"])
        assert dao.currentMatiere == a["matiere"]

    def test_currentPageChanged_With_ZERO(self, dao, fk, qtbot):
        a = fk.f_page(td=True)
        dao._currentPage = "mk"

        with qtbot.waitSignal(dao.updateRecentsAndActivites):
            dao.currentPage = ""

        assert dao.pageModel.page == None
        assert dao.currentMatiere == ""  # a["matiere"]

    def test_updateRecentsAndActivites(self, dao, qtbot):
        with qtbot.waitSignals([dao.recentsModelChanged, dao.pagesParSectionChanged]):
            dao.updateRecentsAndActivites.emit()

    def test_currentMaterieResed(self, fk, dao):
        m = fk.f_matiere()
        a = fk.f_page()
        dao.currentPage = str(a.id)
        dao.matiereReset.emit()
        assert dao.currentPage == ""

    def test_changeAnnee(self, dao, fk, qtbot):
        # setup
        assert dao.annee_active == 2019
        fk.f_annee(2020)
        g = fk.f_groupeMatiere(annee=2019)
        m = fk.f_matiere(groupe=g.id)
        ac = fk.f_activite(matiere=m)
        p = fk.f_page(activite=ac.id, created=datetime.now())
        dao.currentPage = str(p.id)
        assert dao.currentMatiere == str(m.id)
        assert len(dao.recentsModel) == 1

        # test
        with qtbot.waitSignal(dao.anneeActiveChanged):
            dao.changeAnnee.emit(2020)
            assert dao.annee_active == 2020
            assert dao.currentPage == ""
            assert dao.currentMatiere == ""
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

    def test_section_added_disable_busyindicator(self, fk, dao, qtbot):
        f = fk.f_page()
        dao.pageModel.slotReset(f.id)
        dao.ui.buzyIndicator = True
        dao.sectionAdded.emit(0, 0)
        assert not dao.ui.buzyIndicator
