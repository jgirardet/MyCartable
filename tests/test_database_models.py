from datetime import datetime, timedelta

from PySide2.QtCore import QUrl
from fixtures import compare, compare_items, ss
from package.database.factory import *
import pytest
from pony.orm import flush, exists, commit


def test_creation_all(ddb):
    an = f_annee()
    a = f_matiere(annee=an)
    f_section()


class TestPage:
    def test_modified(self, ddb):
        avant = datetime.utcnow()
        s = f_page(created=datetime.utcnow())
        s.to_dict()  # flush
        apres = datetime.utcnow()
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
        assert all(x.modified > datetime.utcnow() - timedelta(days=30) for x in recents)
        old = recents[0]
        for i in recents[1:]:
            assert old.modified > i.modified
            old = i

        # formatted result
        # m = f_matiere()
        # ac = f_activite(matiere=m)
        a = f_page(created=datetime.utcnow())
        res = a.to_dict()
        res["matiere"] = a.activite.matiere.id
        first_dict = db.Page.recents()[0]
        assert first_dict == res

    def test_to_dict(self, ddb):
        d = datetime.utcnow()
        p = f_page(created=d, titre="bl")
        assert p.to_dict() == {
            "id": 1,
            "created": d.isoformat(),
            "modified": d.isoformat(),
            "titre": "bl",
            "activite": p.activite.id,
            "matiere": p.activite.matiere.id,
            "matiereNom": p.activite.matiere.nom,
            "famille": p.activite.famille,
            "lastPosition": p.lastPosition,
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

    # def test_page_par_section(self, ddbr):
    #     m = f_matiere()
    #     a = b_page(5, matiere=m.id)
    #     with db_session:
    #         q = ddbr.Page.page_par_section(m.id)
    #         import itertools
    #         from operator import attrgetter
    #
    #         print(list(q))
    #         # r = itertools.groupby(q, attrgetter("activite"))
    #         # print(q[:])
    #         # r = q
    #         # for x in r:
    #         #     print(x)
    #         #     for y in x:
    #         #         print(y)
    #         #         print(y.to_dict())
    #     assert False


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
        f_matiere().to_dict()  # forcer une creation d'id
        a = f_matiere(nom="Géo")
        pages = [b_page(3, matiere=2) for x in a.activites]
        assert a.to_dict() == {
            "id": 2,
            "nom": "Géo",
            "annee": 2,
            "activites": [4, 5, 6],
        }

    def test_activite_auto_create_after_insert(self, ddb):
        a = f_matiere()
        len(a.activites) == ddb.Activite.ACTIVITES

    def test_page_par_section(self, ddbr):
        f_matiere(nom="Math")
        pages = [
            {
                "created": "2019-03-14T17:35:58.111997",
                "modified": "2019-03-14T17:35:58.111997",
                "titre": "quoi amener défendre charger seulement",
                "activite": 1,
                "lastPosition": None,
            },
            {
                "created": "2019-10-30T10:54:18.834326",
                "modified": "2019-10-30T10:54:18.834326",
                "titre": "sujet grandir emporter monter rencontrer",
                "activite": 3,
                "lastPosition": None,
            },
            {
                "created": "2019-08-17T21:33:55.644158",
                "modified": "2019-08-17T21:33:55.644158",
                "titre": "oreille blague soleil poursuivre riche",
                "activite": 1,
                "lastPosition": None,
            },
            {
                "created": "2020-02-18T22:25:14.288186",
                "modified": "2020-02-18T22:25:14.288186",
                "titre": "enfer cette simple ensemble rendre",
                "activite": 3,
                "lastPosition": None,
            },
            {
                "created": "2019-09-16T03:57:38.860509",
                "modified": "2019-09-16T03:57:38.860509",
                "titre": "grand-père monde cœur reposer rappeler",
                "activite": 1,
                "lastPosition": None,
            },
        ]
        with db_session:
            for p in pages:
                ddbr.Page(**p)
        with db_session:
            mm = ddbr.Matiere[1]
            q = mm.pages_par_section()
            assert q == [
                {
                    "famille": 0,
                    "id": 1,
                    "matiere": 1,
                    "nom": "Leçons",
                    "pages": [
                        {
                            "activite": 1,
                            "created": "2019-09-16T03:57:38.860509",
                            "famille": 0,
                            "id": 5,
                            "lastPosition": None,
                            "matiere": 1,
                            "matiereNom": "Math",
                            "modified": "2019-09-16T03:57:38.860509",
                            "titre": "grand-père monde cœur reposer rappeler",
                        },
                        {
                            "activite": 1,
                            "created": "2019-08-17T21:33:55.644158",
                            "famille": 0,
                            "id": 3,
                            "lastPosition": None,
                            "matiere": 1,
                            "matiereNom": "Math",
                            "modified": "2019-08-17T21:33:55.644158",
                            "titre": "oreille blague soleil poursuivre riche",
                        },
                        {
                            "activite": 1,
                            "created": "2019-03-14T17:35:58.111997",
                            "famille": 0,
                            "id": 1,
                            "lastPosition": None,
                            "matiere": 1,
                            "matiereNom": "Math",
                            "modified": "2019-03-14T17:35:58.111997",
                            "titre": "quoi amener défendre charger seulement",
                        },
                    ],
                },
                {"famille": 1, "id": 2, "matiere": 1, "nom": "Exercices", "pages": []},
                {
                    "famille": 2,
                    "id": 3,
                    "matiere": 1,
                    "nom": "Evaluations",
                    "pages": [
                        {
                            "activite": 3,
                            "created": "2020-02-18T22:25:14.288186",
                            "famille": 2,
                            "id": 4,
                            "lastPosition": None,
                            "matiere": 1,
                            "matiereNom": "Math",
                            "modified": "2020-02-18T22:25:14.288186",
                            "titre": "enfer cette simple ensemble rendre",
                        },
                        {
                            "activite": 3,
                            "created": "2019-10-30T10:54:18.834326",
                            "famille": 2,
                            "id": 2,
                            "lastPosition": None,
                            "matiere": 1,
                            "matiereNom": "Math",
                            "modified": "2019-10-30T10:54:18.834326",
                            "titre": "sujet grandir emporter monter rencontrer",
                        },
                    ],
                },
            ]


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
    def test_to_dict(self, ddbr):
        a = datetime.utcnow()
        x = f_section(created=a, td=True)
        assert x["created"] == a.isoformat()
        assert x["modified"] == a.isoformat()

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
        f_section(page=a.id, created=datetime.utcnow())
        assert page_modified < a.modified

    def test_before_update(self, ddb):
        a = f_section()
        b = a.modified
        a.created = datetime.utcnow()
        flush()
        assert a.modified > b
        assert a.page.modified == a.modified

    def test_before_insert(self, ddbr):
        avant = datetime.utcnow()
        s = f_section(created=datetime.utcnow())
        apres = datetime.utcnow()
        assert avant < s.created < apres
        assert s.created == s.modified
        with db_session:
            assert ddbr.Page[s.page.id].modified >= s.modified

    def test_update_position_on_delete(self, ddbr):
        p = f_page()
        s1 = f_section(page=p.id, position=1)
        s2 = f_section(page=p.id, position=2)
        s3 = f_section(page=p.id, position=3)

        with db_session:
            now = ddbr.Page[p.id].modified
            ddbr.Section[s2.id].delete()

        with db_session:
            # resultat avec décalage
            ddbr.Section[s1.id].position == 1
            ddbr.Section[s3.id].position == 2
            # page mis à jour
            assert now < ddbr.Page[p.id].modified


class TestImageSection:
    def test_factory(self):
        a = f_imageSection(path="/mon/path")
        assert a.path == "/mon/path"

    def test_to_dict(self):
        a = f_imageSection(path="/mon/path", td=True)
        assert a["path"] == str(FILES / "/mon/path")

    def test_path_accept_qpath_and_Pathlib(self):
        assert f_imageSection(path=QUrl(__file__)).path == str(Path(__file__))
        assert f_imageSection(path=Path(__file__)).path == str(Path(__file__))


class TestTextSection:
    def test_factory(self):
        assert f_textSection(text="bla").text == "bla"


class TestOperationSection:
    def test_init(self, ddb):
        f_page()
        # normal
        a = ddb.OperationSection(datas=[[1, 2]], page=1)
        assert a._datas == "[[1,2]]"
        assert a.datas == [[1, 2]]

        # strip spaces
        a = ddb.OperationSection(datas=[[1, 2]], page=1)
        assert a._datas == "[[1,2]]"
        assert a.datas == [[1, 2]]

        # setter
        a.datas = [[3, 4]]
        assert a.datas == [[3, 4]]
        assert a._datas == "[[3,4]]"

        # do not use data if None
        a = ddb.OperationSection(page=1)

        # defautl valut
        a = ddb.OperationSection(page=1)
        assert a.datas == []

    def test_to_dict(self, reset_db):
        item = f_additionSection(datas="259+135", td=True)
        assert item == {
            "classtype": "AdditionSection",
            "created": item["created"],
            "datas": [
                ["", "", "", ""],
                ["", "2", "5", "9"],
                ["+", "1", "3", "5"],
                ["", "", "", ""],
            ],
            "id": 1,
            "modified": item["modified"],
            "page": 1,
            "position": 1,
        }


class TestAddditionSection:
    def test_factory(self):
        assert f_additionSection(datas="15+3").datas == [
            ["", "", ""],
            ["", "1", "5"],
            ["+", "", "3"],
            ["", "", ""],
        ]
        f_additionSection()


class TestAnnotations:
    def test_factory_stabylo(self, ddbr):
        a = f_stabylo()
        isinstance(a, db.Stabylo)
        a = f_stabylo(0.30, 0.40, 0.50, 0.60, td=True)
        print(a)
        assert list(a.values()) == [2, 0.3, 0.4, 2, None, "Stabylo", 0.5, 0.6]

    def test_factory_annotationtext(self, ddbr):
        a = f_annotationText()
        isinstance(a, db.AnnotationText)
        a = f_annotationText(0.30, 0.40, "coucou", td=True)
        print(a)
        assert list(a.values()) == [
            2,
            0.3,
            0.4,
            2,
            None,
            "AnnotationText",
            "coucou",
            False,
        ]

    def test_create_annotation_accept_qcolor(self, ddbr):
        s = f_section()
        with db_session:
            item = ddbr.Stabylo(
                relativeX=0.5,
                relativeY=0.5,
                relativeWidth=0.5,
                relativeHeight=0.5,
                section=s.id,
                color=QColor("red"),
            )
            assert item.color == QColor("red").rgba()

            # test with simple wrga int
            item = ddbr.Stabylo(
                relativeX=0.5,
                relativeY=0.5,
                relativeWidth=0.5,
                relativeHeight=0.5,
                section=s.id,
                color=QColor("red").rgba(),
            )
            assert item.color == QColor("red").rgba()

    def test_annotatation_to_dict(self, ddbr):
        a = f_stabylo(td=True, color="red")
        assert isinstance(a["color"], QColor)
        assert a["color"] == QColor("red")

        # None case
        a = f_stabylo(td=True, color=None)
        assert a["color"] is None

    def test_annotatationText_to_dict(self, ddbr):
        a = f_annotationText(td=True, color="red", underline=True)
        assert isinstance(a["color"], QColor)
        assert a["color"] == QColor("red")
        assert a["underline"] == True

        # None case
        a = f_stabylo(td=True, color=None)
        assert a["color"] is None

    def test_add_modify_section_and_page_modified_attribute(self, ddbr):
        p = f_page()
        before_p = p.modified
        s = f_section(page=p.id, created=datetime.utcnow())
        before = s.modified

        a = f_annotationText(section=s.id)

        with db_session:
            n = ddbr.Section[s.id]
            after = n.modified
            after_p = n.page.modified

        assert before < after
        assert before_p < after_p

    def test_delete_modify_section_and_page_modified_attribute(self, ddbr):
        p = f_page()
        s = f_section(page=p.id, created=datetime.utcnow())
        a = f_annotationText(section=s.id)

        with db_session:
            n = ddbr.Section[s.id]
            before = n.modified
            before_p = n.page.modified

        with db_session:
            ddbr.Annotation[a.id].delete()

        with db_session:
            n = ddbr.Section[s.id]
            after = n.modified
            after_p = n.page.modified

        assert before < after
        assert before_p < after_p

    def test_delete_not_fail_if_section_deleted(self, ddbr):
        a = f_annotationText()
        with db_session:
            s = ddbr.Section[1]
            a = ddbr.Annotation[1]
            s.delete()
            a.delete()
