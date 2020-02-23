import pytest
from PySide2.QtCore import QUrl
from fixtures import compare, ss, check_args
from package import constantes
from package.database_mixins.matiere_mixin import MatieresDispatcher
from package.database_mixins.page_mixin import PageMixin
from package.database_object import DatabaseObject
from package.database.factory import *
from unittest.mock import patch, call

from pony.orm import exists, make_proxy


class TestPageMixin:
    def test_init(self, ddbr):
        a = DatabaseObject(ddbr)
        assert a._currentPage == 0
        assert a._currentTitre == ""
        assert a._currentEntry == None
        assert a.timer_titre.isSingleShot()

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
        with patch.object(d.timer_titre, "start") as m:
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

    def test_on_pagechanged_reset_model(self, dao):
        p1 = f_page()
        f_section(page=p1.id)
        dao.currentPage = p1.id
        assert len(dao.pageModel._datas) == 1

    def test_removePAge(self, dao):
        f_page()
        dao.removePage(1)
        with db_session:
            assert not dao.db.Page.get(id=1)

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

    def test_pagesParSection(self, ddbr, dao):
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


class TestSectionMixin:
    def test_loadsection_image(self, dao):
        s = f_imageSection()
        b_stabylo(5, section=s.id)
        res = dao.loadSection(s.id)
        assert res["id"] == 1
        assert res["path"] == str(FILES / s.path)
        assert len(res["annotations"]) == 5

    def test_loadsection_image_false(self, dao):
        res = dao.loadSection(99999)
        assert res == {}

    @pytest.mark.parametrize(
        "page, content, res, signal_emitted",
        [
            (
                1,
                {
                    "path": "tests/resources/tst_AnnotableImage.png",
                    "classtype": "ImageSection",
                },
                1,
                True,
            ),
            (
                1,
                {
                    "path": QUrl("tests/resources/tst_AnnotableImage.png"),
                    "classtype": "ImageSection",
                },
                1,
                True,
            ),
            (1, {"path": "/my/path", "classtype": "ImageSection"}, 0, False),
            (1, {"classtype": "TextSection"}, 1, False),
            (1, {"classtype": "ImageSection"}, 0, False),
        ],
    )
    def test_addSection(self, dao, ddbn, qtbot, page, content, res, signal_emitted):
        f_page()
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
                if i == "path":
                    assert content[i] != getattr(item, i)
                    assert (FILES / item.path).exists()
                else:
                    assert content[i] == getattr(item, i)

    def test_removeSection(self, dao):
        r = [f_imageSection(), f_textSection()]
        for x in r:
            dao.removeSection(x.id, 99)
        with db_session:
            assert len(dao.db.Section.select()) == 0

    def test_removeSection_signal(self, dao, qtbot):
        r = f_imageSection()
        with db_session:
            item = dao.db.Section[1]
            item.position = 8

        with qtbot.waitSignal(dao.sectionRemoved, check_params_cb=lambda x: (8, 99)):
            dao.removeSection(r.id, 99)


class TestImageSectionMixin:
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
                "color": 123123123,
            },
            {
                "classtype": "Stabylo",
                "section": 1.0,
                "relativeX": 0.3,
                "relativeY": 0.4,
                "relativeWidth": 0.5,
                "relativeHeight": 0.6,
                "color": QColor(123123123),
            },
            {
                "classtype": "AnnotationText",
                "section": 1.0,
                "relativeX": 0.3,
                "relativeY": 0.4,
                "text": "",
                "color": 123123123,
                "underline": None,
            },
        ],
    )
    def test_addAnnotation(self, ddbr, content):
        d = DatabaseObject(ddbr)
        s = f_imageSection()

        res = d.addAnnotation(content)

        with db_session:
            item = s.annotations.select()[:][0].to_dict()
            assert item.pop("id") == res
            assert item.pop("section") == s.id
            assert item == content

            # check modified ok
            item = s.annotations.select()[:][0]
            section = db.Section[s.id]
            assert item.section.page.modified > section.modified

    def test_loadAnnotations(self, dao):
        s = f_imageSection()
        b_stabylo(5, section=s.id)
        res = dao.loadAnnotations(s.id)
        assert len(res) == 5

    def test_udate_annotations_args(self, dao):
        check_args(dao.updateAnnotation, (int, dict))

    @pytest.mark.parametrize(
        "key,value,res",
        [
            ("text", "bla", None),
            ("color", QColor(123123123), None),
            ("underline", QColor("red"), True),
        ],
    )
    def test_updateAnnotationText(self, dao, ddbn, key, value, res):

        a = f_annotationText()
        dao.updateAnnotation(a.id, {"type": key, "value": value})
        with db_session:
            assert getattr(ddbn.Annotation[a.id], key) == res or value

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
                (d.pagesParSectionChanged, "pagesparsection"),
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
                (d.pagesParSectionChanged, "activites"),
                (d.recentsModelChanged, "recentchanged"),
            ]
        ):
            d.currentTitreChanged.emit()

    def test_onSectionAdded(self, dao, ddbn):
        p = f_page()
        s1 = f_section(page=p.id)
        s2 = f_section(page=p.id)
        assert s1.position == 1
        newid = dao.addSection(p.id, {"classtype": "TextSection"})
        with db_session:
            item = ddbn.Section[newid]
            assert item.position == 3
        dao.pageModel.slotReset(p.id)
        assert len(dao.pageModel._datas) == 3
        assert dao.pageModel._datas[item.position - 1]["id"] == item.id

    def test_currentPageChanged(self, dao, ddbr, qtbot):
        a = f_page(td=True)
        with qtbot.wait_signals(
            [
                (dao.pageModel.modelReset, "model"),
                (dao.currentMatiereChanged, "matiere"),
                (dao.pagesParSectionChanged, "activite"),
            ],
            timeout=2000,
        ):
            dao.currentPage = 1
        assert dao.currentMatiere == a["matiere"]
