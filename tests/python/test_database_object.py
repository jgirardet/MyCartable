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
from mycartable.classeur import create_operation
from package.cursors import build_one_image_cursor
from fixtures import check_args
from package import constantes
from package.database_object import DatabaseObject
from unittest.mock import patch, call

from package.files_path import FILES
from pony.orm import ObjectNotFound, db_session


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
                (d.pagesParActiviteChanged, "activites"),
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
                (dao.pagesParActiviteChanged, "activite"),
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
        with qtbot.waitSignals([dao.recentsModelChanged, dao.pagesParActiviteChanged]):
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
        with qtbot.waitSignal(dao.pagesParActiviteChanged):
            dao.pageActiviteChanged.emit()

    def test_section_added_disable_busyindicator(self, fk, dao, qtbot):
        f = fk.f_page()
        dao.pageModel.slotReset(f.id)
        dao.ui.buzyIndicator = True
        dao.sectionAdded.emit(0, 0)
        assert not dao.ui.buzyIndicator
