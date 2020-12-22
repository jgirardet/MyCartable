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
from mycartable import constantes
from package.database_object import DatabaseObject
from unittest.mock import patch, call

from mycartable.files_path import FILES
from pony.orm import ObjectNotFound, db_session


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
