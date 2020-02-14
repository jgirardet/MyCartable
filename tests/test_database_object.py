import pytest
from fixtures import compare, ss, check_args
from package import constantes
from package.database_mixins.matiere_mixin import MatieresDispatcher
from package.database_mixins.page_mixin import PageMixin
from package.database_object import DatabaseObject
from package.database.factory import *
from unittest.mock import patch, call

from pony.orm import exists


class TestPageMixin:
    def test_init(self, ddbr):
        a = DatabaseObject(ddbr)
        assert a._currentPage == 0
        assert a._currentTitre == ""
        assert a._currentEntry == None
        assert a.titreTimer.isSingleShot()

    def test_newPage(self, ddbr, qtbot):
        a = DatabaseObject(ddbr)
        f = f_page()  # pour avoir plusieurs dans le resultats
        with qtbot.wait_signal(a.newPageCreated, timeout=100):
            r = a.newPage(f.activite.id)
        # assert a.currentMatiere == r['matiere']
        # assert a.currentPage == r['id']
        # assert a.activites_all[f.activite.famille][0] == r

    def test_currentPage(self, ddbr, qtbot):
        a = f_page()
        b = f_page()
        c = DatabaseObject(ddbr)
        assert c.currentPage == 0

        # setCurrentPage
        c.currentPage = 1
        assert c.currentPage == a.id
        with qtbot.wait_signal(c.currentPageChanged, timeout=100):
            c.currentPage = 2
        assert c.currentPage == c.currentPage

        # set currentpage do nothing if same id
        with qtbot.assertNotEmitted(c.currentPageChanged):
            c.currentPage = 2
        assert c.currentPage == b.id

    def test_current_entry(self, ddbr):
        a = f_page()
        d = DatabaseObject(ddbr)
        d.currentPage = 1
        with db_session:
            assert d._currentEntry.titre == a.titre == d._currentTitre == d.currentTitre

    def test_CurrentTitreSet(self, ddbr):
        b_page(2)
        d = DatabaseObject(ddbr)

        # case no current page
        d.currentTitre = "omk"
        assert d._currentTitre == ""
        d.currentPage = 1
        with patch.object(d.titreTimer, "start") as m:
            d.currentTitre = "mokmk"
            assert d.currentTitre == "mokmk"
            assert m.call_args_list == [call(500)]

            # do not call storage if same value
            d.currentTitre = "mokmk"
            assert m.call_args_list == [call(500)]

    def test_UnderscoreCurrentTitreSet(self, ddbr, qtbot):
        f_page()
        d = DatabaseObject(ddbr)
        d.currentPage = 1
        d.TITRE_TIMER_DELAY = 0
        with qtbot.wait_signal(d.currentTitreChanged):
            d.currentTitre = "aaa"
        with db_session:
            assert ddbr.Page[1].titre == "aaa"


class TestMatiereMixin:
    def create_matiere(self):
        f_matiere("un")
        f_matiere("deux")
        f_matiere("trois")
        f_matiere("quatre")

    def test_init(self, ddb):
        a = DatabaseObject(ddb)
        assert a._currentMatiere == 0
        assert isinstance(a.m_d, MatieresDispatcher)

    def test_currentMatiere(self, ddbr, qtbot):
        self.create_matiere()
        a = DatabaseObject(ddbr)
        assert a.currentMatiere == 0

        # from int
        with qtbot.waitSignal(a.currentMatiereChanged, timeout=100):
            a.currentMatiere = 2
        a.currentMatiere = 2  # same
        assert a.currentMatiere == 2
        a.currentMatiere = "fez"  # not in do nothing
        assert a.currentMatiere == 2

        # from index
        a.setCurrentMatiereFromIndex(2)
        assert a.currentMatiere == 3

        # get index from id
        assert a.getMatiereIndexFromId(3) == 2
        assert a.getMatiereIndexFromId(99999) is None

    def test_matiereList(self, ddbr):
        self.create_matiere()

        # listnom
        a = DatabaseObject(ddbr)
        assert a.matieresListNom == ("un", "deux", "trois", "quatre")

        # refresh
        f_matiere("cinq")
        a.matieresListRefresh()
        assert a.matieresListNom == ("un", "deux", "trois", "quatre", "cinq")


class TestActiviteMixin:
    def test_lists(self, ddbr):
        un = f_matiere()
        deux = f_matiere()
        b_page(10, matiere=un.id)
        b_page(10, matiere=deux.id)
        a = DatabaseObject(ddbr)
        a.currentMatiere = 2
        for ac, lalist in zip(ACTIVITES, a.activites_all):
            assert all(i["famille"] == ac.index for i in lalist)
            assert all(i["matiere"] == 2 for i in lalist)

    def testupdate(self, ddbr, qtbot):
        a = DatabaseObject(ddbr)
        with qtbot.waitSignals(a.activites_signal_all, timeout=100):
            a.update_activites()


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


class TestSectionMixin:
    def test_loadsection_image(self, dao):
        s = f_imageSection()
        b_stabylo(5, section=s.id)
        res = dao.loadSection(s.id)
        assert res["id"] == 1
        assert res["path"] == str(FILES / s.path)
        assert len(res["annotations"]) == 5

    def test_loadsection_image_false(self, dao):
        # s = f_imageSection()
        # b_stabylo(5, section=s.id)
        res = dao.loadSection(99999)
        assert res == {}
        # assert res["id"] == 1
        # assert res["path"] == str(FILES / s.path)
        # assert len(res["annotations"]) == 5


class TestImageSectionMixin:
    def test_addAnnotation(self, ddbr):
        d = DatabaseObject(ddbr)
        s = f_imageSection()

        # stabylo
        content = {
            "classtype": "Stabylo",
            "section": 1.0,
            "relativeX": 0.3,
            "relativeY": 0.4,
            "relativeWidth": 0.5,
            "relativeHeight": 0.6,
            "color": 123123123,
        }
        res = d.addAnnotation(content)

        with db_session:
            item = s.annotations.select()[:][0].to_dict()
            assert item.pop("id") == res
            assert item.pop("section") == s.id
            assert item == content

        # annotatinotext
        content = {
            "classtype": "AnnotationText",
            "section": 1.0,
            "relativeX": 0.3,
            "relativeY": 0.4,
            "text": "",
            "color": 123123123,
            "underline": None,
        }
        res = d.addAnnotation(content)

        with db_session:
            item = s.annotations.select()[:][1].to_dict()
            assert item.pop("id") == res
            assert item.pop("section") == s.id
            assert item == content

    def test_loadAnnotations(self, dao):
        s = f_imageSection()
        b_stabylo(5, section=s.id)
        res = dao.loadAnnotations(s.id)
        assert len(res) == 5

    def test_udate_annotations_args(self, dao):
        check_args(dao.updateAnnotation, (int, dict))

    @pytest.mark.parametrize(
        "key,value",
        [
            ("text", "bla"),
            ("color", QColor(123123123)),
            ("underline", QColor(123123123)),
        ],
    )
    def test_updateAnnotationText(self, dao, ddbn, key, value):

        a = f_annotationText()
        dao.updateAnnotation(a.id, {"type": key, "value": value})
        with db_session:
            assert getattr(ddbn.Annotation[a.id], key) == value

    @pytest.mark.parametrize("key,value", [("color", QColor(123123123))])
    def test_updateAnnotationStabylo(self, dao, ddbn, key, value):

        a = f_stabylo()
        dao.updateAnnotation(a.id, {"type": key, "value": value})
        with db_session:
            assert getattr(ddbn.Annotation[a.id], key) == value

    def test_deleteAnnotation(self, dao, ddbn):
        check_args(dao.deleteAnnotation, int)

        a = f_annotationText()
        b = f_stabylo()

        c = dao.deleteAnnotation(a.id)
        d = dao.deleteAnnotation(b.id)

        with db_session:
            assert not ddbn.Annotation.exists(id=a.id)
            assert not ddbn.Annotation.exists(id=b.id)


class TestDatabaseObject:
    def test_currentMatiereChanged_all_activite_signals_emited(self, ddbr, qtbot):
        f_matiere()
        d = DatabaseObject(ddbr)
        with qtbot.wait_signals(
            [
                (d.lessonsListChanged, "lessonslistchanged"),
                (d.exercicesListChanged, "exercicelistchanged"),
                (d.evaluationsListChanged, "evaluationslistchanged"),
            ],
        ):
            d.currentMatiere = 1

    def test_RecentsItem_Clicked(self, ddbr, qtbot):
        rec1 = f_page(created=datetime.now(), td=True)
        d = DatabaseObject(ddbr)
        d.recentsItemClicked.emit(rec1["id"], rec1["matiere"])
        assert d.currentMatiere == rec1["matiere"]
        assert d.currentPage == rec1["id"]

    def test_onNewPageCreated(self, ddbr, qtbot):
        a = f_page(td=True, activite="1")
        d = DatabaseObject(ddbr)
        with qtbot.wait_signals(
            [
                (d.exercicesListChanged, "listchanged"),
                (d.recentsModelChanged, "modelreset"),
            ]
        ):
            d.onNewPageCreated(a)
        assert d.currentPage == a["id"]
        assert d.currentMatiere == a["matiere"]

    def test_onCurrentTitreChanged(self, ddbr, qtbot):
        a = f_page(td=True, activite="1")
        d = DatabaseObject(ddbr)
        with qtbot.wait_signals(
            [
                (d.exercicesListChanged, "listchanged"),
                (d.recentsModelChanged, "modelreset"),
            ]
        ):
            d.currentTitreChanged.emit()
