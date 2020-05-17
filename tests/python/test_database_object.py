import logging
import sys
import uuid

import pytest
from PIL import Image
from PySide2.QtCore import QUrl, Qt, QModelIndex
from fixtures import compare, ss, check_args, wait
from package import constantes
from package.database_mixins.matiere_mixin import MatieresDispatcher
from package.database_object import DatabaseObject
from package.database.factory import *
from unittest.mock import patch, call
from package.files_path import FILES


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


class TestMatiereMixin:
    def create_matiere(self):
        gp = f_groupeMatiere()
        f_matiere(
            "un", annee=2019, _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id
        )
        f_matiere(
            "deux", annee=2019, _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id
        )
        f_matiere(
            "trois", annee=2019, _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id
        )
        f_matiere(
            "quatre", annee=2019, _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id
        )

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
        assert dao.getMatiereIndexFromId(99999) is None

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
                "annee": 2019,
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "id": 1,
                "groupe": 1,
                "nom": "un",
            },
            {
                "activites": [4, 5, 6],
                "annee": 2019,
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": 1,
                "id": 2,
                "nom": "deux",
            },
            {
                "activites": [7, 8, 9],
                "annee": 2019,
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": 1,
                "id": 3,
                "nom": "trois",
            },
            {
                "activites": [10, 11, 12],
                "annee": 2019,
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": 1,
                "id": 4,
                "nom": "quatre",
            },
        ]
        assert dao.matieresList == reslist

        # refresh
        f_matiere("cinq", annee=2019, _fgColor=4294967295, _bgColor=4294901760)
        dao.matieresListRefresh()
        reslist.append(
            {
                "activites": [13, 14, 15],
                "annee": 2019,
                "bgColor": QColor("red"),
                "fgColor": QColor("white"),
                "groupe": 2,
                "id": 5,
                "nom": "cinq",
            }
        )
        assert dao.matieresList == reslist

    def test_pagesParSection(self, dao):
        assert dao.pagesParSection == []
        f_matiere()
        p = f_page(td=True, activite=3)
        dao.currentMatiere = 1
        assert dao.pagesParSection[0]["id"] == 1
        assert dao.pagesParSection[0]["famille"] == 0
        assert dao.pagesParSection[1]["famille"] == 1
        assert dao.pagesParSection[1]["id"] == 2
        assert dao.pagesParSection[2]["famille"] == 2
        assert dao.pagesParSection[2]["id"] == 3
        assert dao.pagesParSection[2]["pages"] == [p]


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
        r = dao.setStyle(a.id, {"underline": True, "bgColor": "red"})
        assert r == {
            "bgColor": QColor("red"),
            "family": "",
            "fgColor": QColor("black"),
            "id": 1,
            "pointSize": None,
            "strikeout": False,
            "underline": True,
            "weight": None,
        }

        with db_session:
            item = dao.db.Style[a.id]
            assert item.bgColor == "red"
            assert item.underline == True

        # bad params
        r = dao.setStyle(a.id, {"badparam": True})
        assert "Unknown attribute 'badparam'" in caplog.records[0].msg
        assert caplog.records[0].levelname == "ERROR"
        caplog.clear()

        # style does not exists
        with db_session:
            b = dao.db.Style[a.id]
            b.delete()

        r = dao.setStyle(a.id, {"underline": True})
        assert (
            caplog.records[0].msg
            == "Echec de la mise à jour du style : ObjectNotFound  Style[1]"
        )
        assert caplog.records[0].levelname == "ERROR"


class TestSectionMixin:
    def test_loadsection_image(self, dao):
        s = f_imageSection(path="bla/ble.jpg")
        b_stabylo(5, section=s.id)
        res = dao.loadSection(s.id)
        assert res["id"] == 1
        assert res["path"] == QUrl.fromLocalFile(str(FILES / "bla/ble.jpg"))
        assert len(res["annotations"]) == 5

    def test_loadsection_image_false(self, dao):
        res = dao.loadSection(99999)
        assert res == {}

    def test_load_section_Operation(self, dao):
        a = f_additionSection(string="3+4")
        assert dao.loadSection(1) == {
            "classtype": "AdditionSection",
            "created": a.created.isoformat(),
            "datas": ["", "", "", "3", "+", "4", "", ""],
            "rows": 4,
            "columns": 2,
            "id": 1,
            "modified": a.modified.isoformat(),
            "page": 1,
            "position": 0,
            "size": 8,
            "virgule": 0,
        }

    def test_load_section_tableau(self, dao):
        a = f_tableauSection(lignes=3, colonnes=3)
        assert dao.loadSection(1) == {
            "cells": [
                (1, 0, 0),
                (1, 0, 1),
                (1, 0, 2),
                (1, 1, 0),
                (1, 1, 1),
                (1, 1, 2),
                (1, 2, 0),
                (1, 2, 1),
                (1, 2, 2),
            ],
            "classtype": "TableauSection",
            "created": a.created.isoformat(),
            "colonnes": 3,
            "id": 1,
            "lignes": 3,
            "modified": a.modified.isoformat(),
            "page": 1,
            "position": 0,
        }

    def test_loadsection_equation(self, dao):
        eq = f_equationSection(content="1+2", td=True)
        print(eq)
        assert dao.loadSection(1) == {
            "classtype": "EquationSection",
            "created": eq["created"],  # .created.isoformat(),
            "content": "1+2",
            "id": 1,
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
        assert a == res
        if res == 0:
            return
        with db_session:
            item = ddbn.Section[1]
            assert item.page.id == 1
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
            # breakpoint()
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
        assert a == res
        if res == 0:
            return
        with db_session:
            item = ddbr.Section[1]
            assert item.page.id == 1
            for i in content.keys():
                if i == "path":
                    assert content[i] == getattr(item, i)
                    assert (FILES / item.path).exists()
                elif i == "string":
                    item.datas == create_operation(content["string"])
                else:
                    assert content[i] == getattr(item, i)

    #
    # def test_removeSection(self, dao, qtbot):
    #     r = [f_imageSection(), f_textSection()]
    #     for x in r:
    #         dao.removeSection(x.id, 99)
    #     with db_session:
    #         assert len(dao.db.Section.select()) == 0
    #
    #     # not item
    #     with qtbot.waitSignal(dao.sectionRemoved, check_params_cb=lambda x: x == 99):
    #         dao.removeSection(9999, 99)
    #
    # def test_removeSection_signal(self, dao, qtbot):
    #     r = f_imageSection()
    #     with db_session:
    #         item = dao.db.Section[1]
    #         item.position = 8
    #
    #     with qtbot.waitSignal(dao.sectionRemoved, check_params_cb=lambda x: (8, 99)):
    #         dao.removeSection(r.id, 99)


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

    @pytest.mark.parametrize(
        "content",
        [
            {
                "classtype": "Stabylo",
                "section": 1.0,
                "relativeX": 0.3,
                "relativeY": 0.4,
                "relativeWidth": 0.5,
                "relativeHeight": 0.6,
            },
            {
                "classtype": "Stabylo",
                "section": 1.0,
                "relativeX": 0.3,
                "relativeY": 0.4,
                "relativeWidth": 0.5,
                "relativeHeight": 0.6,
                "style": {"bgColor": "red"},
            },
            {
                "classtype": "AnnotationText",
                "section": 1.0,
                "relativeX": 0.3,
                "relativeY": 0.4,
                "text": "",
                # "underline": None,
            },
        ],
    )
    def test_addAnnotation(self, dao, content):
        s = f_imageSection()
        wait()
        c_style = {}
        if "style" in content:
            c_style = dict(content["style"])

        item = dao.addAnnotation(content)
        with db_session:
            item = s.annotations.select()[:][0].to_dict()
            assert item.pop("id")
            assert item.pop("section") == s.id
            style = item.pop("style")
            if c_style:
                c_style = content.pop("style")
                for k, v in c_style.items():
                    assert style[k] == v

            assert item == content

    def test_loadAnnotations(self, dao):
        s = f_imageSection()
        b_stabylo(5, section=s.id)
        res = dao.loadAnnotations(s.id)
        assert len(res) == 5

    def test_update_annotations_args(self, dao):
        check_args(dao.updateAnnotation, (int, dict), dict)

    @pytest.mark.parametrize(
        "genre, content",
        [
            ("AnnotationText", {"text": "bla"}),
            ("AnnotationText", {"style": {"underline": True}}),
            (
                "AnnotationText",
                {"style": {"fgColor": QColor("red")}, "text": "oiuouoi"},
            ),
            ("Stabylo", {"relativeWidth": 0.3, "style": {"strikeout": True}}),
        ],
    )
    def test_updateAnnotation(self, dao, ddbn, genre, content):

        from package.database import factory

        fn = "f_" + genre[0].lower() + genre[1:]
        a = getattr(factory, fn)()
        res = dao.updateAnnotation(a.id, content)
        with db_session:
            item = ddbn.Annotation[a.id]
            assert res == item.to_dict(exclude=["style"])
            for k, v in content.items():
                if k == "style":
                    for i, j in v.items():
                        assert getattr(item.style, i) == j
                else:
                    assert getattr(item, k) == v

    def test_update_annotation_update_recents(self, dao, ddbr, qtbot):

        x = f_annotationText()
        with qtbot.wait_signal(dao.imageChanged):
            dao.updateAnnotation(x.id, {"relativeX": 0.33715596330275227})

    def test_delete_annotation_emit_image_changed(self, dao, ddbr, qtbot):

        # pas de text pas d'emit
        x = f_annotationText(text="empty")
        with qtbot.assert_not_emitted(dao.imageChanged):
            dao.deleteAnnotation(x.id)

        # pas de taille, pas d'emit
        x = f_stabylo(relativeWidth=0, relativeHeight=0)
        with db_session:
            ddbr.Stabylo[x.id].relativeWidth = 0
            ddbr.Stabylo[x.id].relativeHeight = 0
        with qtbot.assert_not_emitted(dao.imageChanged):
            dao.deleteAnnotation(x.id)

        # cas usuel ok
        x = f_annotationText(text="bla")
        with qtbot.wait_signal(dao.imageChanged):
            dao.deleteAnnotation(x.id)

    def test_deleteAnnotation(self, dao, ddbn):
        check_args(dao.deleteAnnotation, int)

        a = f_annotationText()
        b = f_stabylo()

        c = dao.deleteAnnotation(a.id)
        d = dao.deleteAnnotation(b.id)

        with db_session:
            assert not ddbn.Annotation.exists(id=a.id)
            assert not ddbn.Annotation.exists(id=b.id)

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


class TestSettingsMixin:
    def test_determine_annee(self, dao):
        # assert False
        assert dao._determine_annee(day=datetime(2016, 3, 3)) == 2015
        assert dao._determine_annee(day=datetime(2016, 9, 3)) == 2016
        assert dao._determine_annee(day=datetime(2016, 1, 1)) == 2015
        assert dao._determine_annee(day=datetime(2016, 8, 15)) == 2016
        assert dao._determine_annee(day=datetime(2016, 8, 14)) == 2015

    def test_get_annee_active(self, dao):
        dao.settings.setValue("General/annee_active", 2030)
        assert dao.get_annee_active() == 2030
        dao.settings.clear()
        assert dao.get_annee_active() == dao._determine_annee()

    def test_setup_settings(self, dao):
        dao.settings.clear()
        dao.setup_settings()
        assert isinstance(dao.annee_active, int)

    def test_getMenuesAnnees(self, dao):
        check_args(dao.getMenuAnnees, None, list)
        for i in range(4):
            f_annee(2016 - (i * i))  # pour tester l'ordre
        assert dao.getMenuAnnees() == [
            {"id": 2007, "niveau": "cm2007"},
            {"id": 2012, "niveau": "cm2012"},
            {"id": 2015, "niveau": "cm2015"},
            {"id": 2016, "niveau": "cm2016"},
            {"id": 2019, "niveau": "cm2019"},  # 2019 setté dans la fixture dao
        ]

    def test_anneActive(self, dao):
        assert dao.anneeActive == 2019


class TestDatabaseObject:
    def test_init_settings(self, ddbr, dao):
        # settings pas inité en mode debug (default
        assert DatabaseObject(ddbr).annee_active is None

        # settings inités en non debug
        with patch.object(DatabaseObject, "setup_settings") as m:
            DatabaseObject(ddbr, debug=False)
            assert m.call_args_list == [call()]

        # init matiere dsi annee_active
        assert isinstance(dao.m_d, MatieresDispatcher)

    def test_RecentsItem_Clicked(self, ddbr, qtbot):
        rec1 = f_page(created=datetime.now(), td=True)
        d = DatabaseObject(ddbr)
        d.recentsItemClicked.emit(rec1["id"], rec1["matiere"])
        assert d.currentMatiere == rec1["matiere"]
        assert d.currentPage == rec1["id"]

    def test_onNewPageCreated(self, ddbr, qtbot):
        a = f_page(td=True, activite="1")
        d = DatabaseObject(ddbr)
        d.onNewPageCreated(a)
        assert d.currentPage == a["id"]
        assert d.currentMatiere == a["matiere"]

    def test_onCurrentTitreSetted(self, ddbr, qtbot):
        a = f_page(td=True, activite="1")
        d = DatabaseObject(ddbr)
        with qtbot.wait_signals(
            [
                (d.pagesParSectionChanged, "activites"),
                (d.recentsModelChanged, "recentchanged"),
            ]
        ):
            d.currentTitreSetted.emit()

    def test_onSectionAdded(self, dao, ddbn):
        p = f_page()
        s1 = f_section(page=p.id)
        s2 = f_section(page=p.id)
        dao.pageModel.slotReset(p.id)
        assert s1.position == 0
        newid = dao.addSection(p.id, {"classtype": "TextSection"})
        with db_session:
            item = ddbn.Section[newid]
            assert item.position == 2
        p = dao.pageModel
        assert p.rowCount() == 3
        assert p.data(p.index(2, 0), p.PageRole)["id"] == item.id

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
        m = f_matiere(annee=2019)
        p = f_page(matiere=m.id, created=datetime.now())
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
