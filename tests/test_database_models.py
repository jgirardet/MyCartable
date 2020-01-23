from datetime import datetime, timedelta

from fixtures import compare
from package.database.factory import *
import pytest
from pony.orm import flush, exists, commit

pytestmark = pytest.mark.usefixtures(*["ddb"])


def test_creation_all():
    an = f_annee()
    a = f_matiere(annee=an)
    f_section()


class TestSection:
    def test_modified(self, ddb):
        # insert
        avant = datetime.now()
        s = f_section(created=datetime.now())
        s.to_dict()  # flush
        apres = datetime.now()
        assert avant < s.created < apres

        # page mis à jours
        assert s.page.modified == s.modified

        # update
        avant = datetime.now()
        s.content = "mkplkù lù pl"
        mod = s.to_dict()["modified"]
        apres = datetime.now()
        assert s.created < avant < mod < apres

        # page mis a jour en même temps  item
        assert s.modified == s.page.modified


class TestPage:
    def test_modified(self):
        avant = datetime.now()
        s = f_page(created=datetime.now())
        s.to_dict()  # flush
        apres = datetime.now()
        assert s.created == s.modified
        assert avant < s.created < apres

    def test_recents(self):

        for i in range(100):
            f_page()
        flush()

        # test query
        assert db.Page.select().count() == 100
        recents = db.Page._query_recents(db.Page)[:]
        assert all(x.modified > datetime.now() - timedelta(days=30) for x in recents)
        old = recents[0]
        for i in recents[1:]:
            assert old.modified > i.modified
            old = i

        # formatted result
        # m = f_matiere()
        # ac = f_activite(matiere=m)
        a = f_page(created=datetime.now())
        res = a.to_dict()
        res["matiere"] = a.activite.matiere.id
        first_dict = db.Page.recents()[0]
        assert first_dict == res

    def test_to_dict(self):
        d = datetime.now()
        p = f_page(created=d, titre="bl")
        assert p.to_dict() == {
            "id": 1,
            "created": d,
            "modified": d,
            "titre": "bl",
            "activite": p.activite.id,
            "matiere": p.activite.matiere.id,
            "matiereNom": p.activite.matiere.nom,
            "activiteIndex": p.activite.famille
        }

    def test_nouvelle_page(self, ddb):
        a = f_matiere().to_dict()
        b = ddb.Page.new_page(activite=1, titre="bla")
        assert ddb.Page.get(id=b["id"], titre="bla", activite=1)


class TestMatiere:
    def test_noms(self, ddb):
        assert ddb.Matiere.select()[:] == []
        f_matiere(nom="a")
        f_matiere(nom="b")
        f_matiere(nom="c")
        f_matiere(nom="d")
        f_matiere(nom="e")
        assert ddb.Matiere.noms() == ["a", "b", "c", "d", "e"]

    def test_to_dict(self, ddb):
        f_matiere().to_dict()
        a = f_matiere(nom="Géo")
        assert a.to_dict() == {'id': 2, 'nom': 'Géo', 'annee': 2, 'activites': [4, 5, 6]}


class TestActivite:
    def test_pages_by_matiere_and_famille(self, ddb):
        m = f_matiere("bla")
        m.to_dict()

        # matiere param is 0
        assert ddb.Activite.pages_by_matiere_and_famille(0, 0) == []

        # No matiere exist:

        pages = ddb.Activite.pages_by_matiere_and_famille(99, 0)
        assert pages == []

        # matiere exist but no activite
        flush()
        pages = ddb.Activite.pages_by_matiere_and_famille(m.id, 99)
        assert pages == []

        # MAtiere existe resuslt empty
        pages = ddb.Activite.pages_by_matiere_and_famille(m.id, 0)
        assert pages == []

        # setup
        controle = []
        controle = [f_page(activite=m.activites.select()[:][0]).to_dict() for i in range(5)]

        # sema matiere different section
        f_page(activite=m.activites.select()[:][1]).to_dict()
        # different matiere
        f_page()

        # with numerique id
        pages = ddb.Activite.pages_by_matiere_and_famille(m.id, 0)
        assert compare(pages, controle)

        # with str id
        pages = ddb.Activite.pages_by_matiere_and_famille("bla", 0)
        assert compare(pages, controle)
        # with str id matiere unknown
        pages = ddb.Activite.pages_by_matiere_and_famille("ble", 0)
        assert compare(pages, [])
