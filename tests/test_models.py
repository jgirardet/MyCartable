from datetime import datetime, timedelta

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
        m = f_matiere()
        ac = f_activite(matiere=m)
        a = f_page(created=datetime.now(), activite=ac)
        res = a.to_dict()
        res["matiere"] = m.id
        first_dict = db.Page.recents()[0]
        assert first_dict == res

    def test_to_dict(self):
        d = datetime.now()
        a = f_activite()
        p = f_page(created=d, titre="bl", activite=a)
        assert p.to_dict() == {
            "id": 1,
            "created": d,
            "modified": d,
            "titre": "bl",
            "activite": 1,
            "matiere": a.matiere.id,
            "matiereNom": a.matiere.nom,
        }

    def test_nouvelle_page(self, ddb):
        a = f_activite()
        a.to_dict()
        b = ddb.Page.new_page(activite=a, titre="bla")
        assert ddb.Page.get(id=b["id"], titre="bla", activite=a)


class TestMatiere:
    def test_noms(self, ddb):
        assert ddb.Matiere.select()[:] == []
        f_matiere(nom="a")
        f_matiere(nom="b")
        f_matiere(nom="c")
        f_matiere(nom="d")
        f_matiere(nom="e")
        assert ddb.Matiere.noms() == ["a", "b", "c", "d", "e"]


class TestActivite:
    def test_pages_by_matiere_and_famille(self, ddb):
        m = f_matiere("bla")
        m.to_dict()
        ac = f_activite(0, m)
        flush()

        pages = ddb.Activite.pages_by_matiere_and_famille(m.id, 0)
        assert pages == []
        controle = []
        for i in range(5):
            controle.append(f_page(activite=ac).to_dict())

        # sema matiere different section
        g = f_activite(1, m)
        f_page(activite=g).to_dict()
        # different matiere
        f_page()

        pages = ddb.Activite.pages_by_matiere_and_famille(m.id, 0)
        for d in pages:
            assert d in controle
        assert len(pages) == len(controle)

