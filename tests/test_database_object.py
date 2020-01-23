from fixtures import compare, ss
from package import constantes
from package.database_mixins.matiere_mixin import MatieresDispatcher
from package.database_mixins.page_mixin import PageMixin
from package.database_object import DatabaseObject
from package.database.factory import *
from unittest.mock import patch

from package.list_models import RecentsModel


class TestPageMixin:

    def test_init(self, ddbr):
        a = DatabaseObject(ddbr)
        assert a._currentPage==0

    def test_newPage(self, ddbr, qtbot):
        a = DatabaseObject(ddbr)
        f = f_page() # pour avoir plusieurs dans le resultats
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

        #setCurrentPage
        c.currentPage = 1
        assert c.currentPage == a.id
        with qtbot.wait_signal(c.currentPageChanged, timeout=100):
            c.currentPage = 2
        assert c.currentPage == b.id


class TestMatiereMixin:
    def create_matiere(self):
        f_matiere("un")
        f_matiere("deux")
        f_matiere("trois")
        f_matiere("quatre")

    def test_init(self,ddb):
        a = DatabaseObject(ddb)
        assert a._currentMatiere == 0
        assert isinstance(a.m_d, MatieresDispatcher)

    def test_currentMatiere(self,ddbr, qtbot):
        self.create_matiere()
        a = DatabaseObject(ddbr)
        assert a.currentMatiere == 0

        # from int
        with qtbot.waitSignal(a.currentMatiereChanged, timeout=100):
            a.currentMatiere = 2
        a.currentMatiere = 2 #same
        assert a.currentMatiere == 2
        a.currentMatiere = "fez" #not in do nothing
        assert a.currentMatiere == 2

        #from index
        a.setCurrentMatiereFromIndex(2)
        assert a.currentMatiere==3


        #get index from id
        assert a.getMatiereIndexFromId(3) == 2
        assert a.getMatiereIndexFromId(99999) is None

    def test_matiereList(self,ddbr):
        self.create_matiere()

        # listnom
        a = DatabaseObject(ddbr)
        assert a.matieresListNom == ("un", "deux", "trois", "quatre")

        #refresh
        f_matiere("cinq")
        a.matieresListRefresh()
        assert a.matieresListNom == ("un", "deux", "trois", "quatre", "cinq")


class TestActiviteMixin:
    def test_lists(self,ddbr):
        populate_database()
        a = DatabaseObject(ddbr)
        a.currentMatiere = 2
        for ac, lalist in zip(ACTIVITES, a.activites_all):
            assert all(i['activiteIndex'] == ac.index for i in lalist)
            assert all(i['matiere'] == 2 for i in lalist)

    def testupdate(self, ddbr, qtbot):
        a = DatabaseObject(ddbr)
        with qtbot.waitSignals(a.activites_signal_all, timeout=100):
            a.update_activites()

class TestRecentsMixin:
    def test_init(self, ddbr):
        d = DatabaseObject(ddbr)
        assert isinstance(d.models['recentsModel'], RecentsModel)
        assert d.recentsModel == d.models['recentsModel']
#

class TestLayoutMixin:
    def test_getlayoutsize(self, dao: DatabaseObject):
        assert dao.getLayoutSizes("preferredCentralWidth") == constantes.preferredCentralWidth
class TestDatabaseObject:

    def test_onOnCurrentMAtiereChanged(self, ddbr):
        populate_database()
        a = DatabaseObject(ddbr)
        a.currentMatiere = 2
        for ac, lalist in zip(ACTIVITES, a.activites_all):
            assert all(i['activiteIndex'] == ac.index for i in lalist)
            assert all(i['matiere'] == 2 for i in lalist)

    def test_RecentsItem_Clicked(self, ddbr):
        populate_database()
        rec = ss(ddbr.Page.recents)
        rec1 = rec[1]
        d = DatabaseObject(ddbr)
        d.recentsItemClicked.emit(rec1['id'], rec1['matiere'])
        assert d.currentMatiere== rec1['matiere']
        assert d.currentPage == rec1['id']

    def test_onNewPageCreated(self, ddbr, qtbot):
        a = f_page(td=True, activite="1")
        d = DatabaseObject(ddbr)
        with qtbot.wait_signal(d.exercicesListChanged):
            d.onNewPageCreated(a)
        assert d.currentPage == a['id']
        assert d.currentMatiere == a['matiere']

# def test_connections(ddbr):
#     m = f_matiere()
#     m2 = f_matiere()
#     a = b_page(10, td=True, activite=m.activites[0])
#     b = b_page(10, td=True, activite=ac2.id)
#     c = b_page(10, td=True, activite=ac3.id)
#     d = DatabaseObject(ddbr)
#     # with patch.object(d, "lessonsListChanged") as s:
#     d.currentMatiere = m.id
#     for j in d.ACTIVITE_LIST:
#         for i in  getattr(d, j):
#             i['matiere'] = m.id