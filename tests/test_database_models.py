from datetime import datetime, timedelta

from fixtures import compare, compare_items
from package.database.factory import *
import pytest
from pony.orm import flush, exists, commit


def test_creation_all(ddb):
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
    def test_modified(self, ddb):
        avant = datetime.now()
        s = f_page(created=datetime.now())
        s.to_dict()  # flush
        apres = datetime.now()
        assert s.created == s.modified
        assert avant < s.created < apres

    def test_update_modified_when_updated(self, ddb):
        a = f_page()
        avant = a.modified
        a.titre = "omkmo"
        flush()
        assert a.modified != avant

    def test_recents(self, ddb):

        for i in range(100):
            f_page()
        # flush()

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

    def test_to_dict(self, ddb):
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
            "activiteIndex": p.activite.famille,
        }

    def test_nouvelle_page(self, ddb):
        a = f_matiere().to_dict()
        b = ddb.Page.new_page(activite=1, titre="bla")
        assert ddb.Page.get(id=b["id"], titre="bla", activite=1)

    def test_content(selfself, ddbr):
        a = f_page()
        sections = b_section(10, page=a.id)
        others = b_section(10)
        with db_session:
            compare_items(a.content, sections)
        prev = None
        with db_session:
            for i in a.content:
                if prev:
                    assert i.position > prev.position
                prev = i


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
        assert a.to_dict() == {
            "id": 2,
            "nom": "Géo",
            "annee": 2,
            "activites": [4, 5, 6],
        }


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
        controle = [
            f_page(activite=m.activites.select()[:][0]).to_dict() for i in range(5)
        ]

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


class TestSection:
    def test_modified(self, ddb):
        """tested in page"""

    def test_before_insert_no_position(self, ddb):
        """"remember factory are flushed"""
        a = f_page()
        b = f_section(page=a.id)
        assert b.position == 1
        c = f_section(page=a.id)
        assert b.position == 1
        assert c.position == 2

    def test_before_insert_position_to_high(self, ddbr):
        a = f_page()
        b = f_section(page=a.id)
        assert b.position == 1
        c = f_section(page=a.id, position=3)
        assert b.position == 1
        assert c.position == 2

    def test_update_position(self, ddb):
        a = f_page()
        b = b_section(5, page=a.id)
        modified_item = b[0].modified
        c = f_section(page=a.id, position=3)

        # test new item
        assert c.position == 3

        # test item existant
        n = 1
        for x in a.content:
            assert x.position == n
            n += 1
        # position n'influence pas la date de modif de section
        assert a.content[0].modified == modified_item

        # inflence l date de modif de page
        page_modified = a.modified
        f_section(page=a.id, created=datetime.now())
        assert page_modified < a.modified

    def test_before_update(self, ddb):
        a = f_section()
        b = a.modified
        a.content = "ùpl"
        flush()
        assert a.modified > b
        assert a.page.modified == a.modified

    def test_to_dict(self, ddb):
        p = f_page()
        d = f_datetime()
        sec = f_section(created=d, page=p.id, img=True)
        s = f_stabylo(0.30, 0.40, 0.50, 0.60, section=sec.id)
        assert sec.to_dict() == {
            "content": "essai.jpg",
            "contentType": "image",
            "created": d,
            "id": 1,
            "modified": d,
            "page": 1,
            "position": 1,
            "annotations": [
                {
                    "classtype": "Stabylo",
                    "relativeHeight": 0.6,
                    "id": 1,
                    "section": 1,
                    "relativeWidth": 0.5,
                    "relativeX": 0.3,
                    "relativeY": 0.4,
                }
            ],
        }


class TestAnnotationsAndStabylos:
    def test_factory_stabylo(self, ddbr):
        a = f_stabylo()
        isinstance(a, db.Stabylo)
        a = f_stabylo(0.30, 0.40, 0.50, 0.60, td=True)
        assert list(a.values()) == [2, 0.3, 0.4, 2, "Stabylo", 0.5, 0.6]

    def test_factory_annotation(self, ddbr):
        a = f_annotationText()
        isinstance(a, db.AnnotationText)
        a = f_annotationText(0.30, 0.40, "coucou", td=True)
        assert list(a.values()) == [
            2,
            0.3,
            0.4,
            2,
            "AnnotationText",
            "coucou",
        ]
