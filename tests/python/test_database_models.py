import itertools
import uuid
from typing import List

from PySide2.QtGui import QFont
from fixtures import compare_items, check_is_range, wait
from factory import *
import pytest
from package.database.mixins import PositionMixin
from package.exceptions import MyCartableOperationError
from pony.orm import flush, Database, make_proxy


def test_creation_all(ddb):
    an = f_annee()
    goupe = f_groupeMatiere(nom="aa", annee=an.id)
    a = f_matiere(groupe=goupe)
    f_section()


class TestAnnee:
    def test_get_matieres(self, ddbr):
        with db_session:
            an = f_annee(id=2017)
            assert an.get_matieres()[:] == []
        with db_session:
            g1 = f_groupeMatiere(annee=2017)
            g2 = f_groupeMatiere(annee=2017)
            g3 = f_groupeMatiere(annee=2015)
            g4 = f_groupeMatiere(annee=2017)
            g5 = f_groupeMatiere(annee=2016)
            a = f_matiere(nom="a", groupe=g1)
            b = f_matiere(nom="b", groupe=g2)
            c = f_matiere(nom="c", groupe=g3)
            d = f_matiere(nom="d", groupe=g4)
            f = f_matiere(nom="e", groupe=g5)
            assert an.get_matieres()[:] == [a, b, d]


class TestPage:
    def test_modified(self, ddb):
        avant = datetime.utcnow()
        wait()
        s = f_page(created=datetime.utcnow())
        s.to_dict()  # flush

        wait()
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
        g2019 = f_groupeMatiere(annee=2019)
        g2018 = f_groupeMatiere(annee=2018)
        m2019 = f_matiere(groupe=g2019)
        m2018 = f_matiere(groupe=g2018)
        ac2019 = f_activite(matiere=m2019.id)
        ac2018 = f_activite(matiere=m2018.id)
        for i in range(50):
            f_page(activite=ac2018.id)
            f_page(activite=ac2019.id)

        # test query
        assert db.Page.select().count() == 100
        recents = db.Page._query_recents(db.Page, 2019)[:]
        assert all(x.modified > datetime.utcnow() - timedelta(days=30) for x in recents)
        assert all(x.activite.matiere.groupe.annee.id == 2019 for x in recents)
        old = recents[0]
        for i in recents[1:]:
            assert old.modified > i.modified
            old = i

        # formatted result
        a = f_page(created=datetime.utcnow(), activite=ac2019.id)
        res = a.to_dict()
        res["matiere"] = str(a.activite.matiere.id)
        first_dict = db.Page.recents(2019)[0]
        assert first_dict == res

    def test_to_dict(self, ddb):
        d = datetime.utcnow()
        p = f_page(created=d, titre="bl")
        assert p.to_dict() == {
            "id": str(p.id),
            "created": d.isoformat(),
            "modified": d.isoformat(),
            "titre": "bl",
            "activite": str(p.activite.id),
            "matiere": str(p.activite.matiere.id),
            "matiereNom": p.activite.matiere.nom,
            "matiereBgColor": p.activite.matiere.bgColor,
            "matiereFgColor": p.activite.matiere.fgColor,
            "lastPosition": p.lastPosition,
        }

    def test_nouvelle_page(self, ddb):
        a = f_matiere().to_dict()
        ac = f_activite(matiere=a["id"])
        flush()
        b = ddb.Page.new_page(activite=ac.id, titre="bla")
        assert ddb.Page.get(id=b["id"], titre="bla", activite=ac.id)

    def test_content(self, ddbr):
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


class TestGroupeMatiere:
    def test_delete_mixin_position(self, reset_db):
        a = f_groupeMatiere(annee=2019)
        b = f_groupeMatiere(annee=2019)
        with db_session:
            assert GroupeMatiere[a.id].position == 0
            assert GroupeMatiere[b.id].position == 1
            GroupeMatiere[a.id].delete()
        with db_session:
            assert GroupeMatiere[b.id].position == 0

    def test_color_mixin(self, reset_db):
        f_annee(id=1234)
        with db_session:
            a = GroupeMatiere(nom="bk", annee=1234)
            b = GroupeMatiere(nom="bk", annee=1234, fgColor="red")
            c = GroupeMatiere(nom="bk", annee=1234, bgColor="green")
        with db_session:
            assert GroupeMatiere[a.id].bgColor == QColor("white")
            assert GroupeMatiere[a.id].fgColor == QColor("black")
            assert GroupeMatiere[b.id].bgColor == QColor("white")
            assert GroupeMatiere[b.id].fgColor == QColor("red")
            assert GroupeMatiere[c.id].bgColor == QColor("green")
            assert GroupeMatiere[c.id].fgColor == QColor("black")
            assert GroupeMatiere[b.id].to_dict()["fgColor"] == QColor("red")
            assert GroupeMatiere[c.id].to_dict()["bgColor"] == QColor("green")


class TestMatiere:
    def test_to_dict(self, ddb):
        f_matiere()
        groupe = f_groupeMatiere(annee=2019)
        a = f_matiere(
            nom="Géo", groupe=groupe, _fgColor=4294967295, _bgColor=4294901760
        )
        pages = [b_page(3, matiere=2) for x in a.activites]
        x = f_activite(matiere=a.id)
        y = f_activite(matiere=a.id)
        z = f_activite(matiere=a.id)
        assert a.to_dict() == {
            "position": 0,
            "id": str(a.id),
            "nom": "Géo",
            "activites": [str(x.id), str(y.id), str(z.id)],
            "groupe": str(groupe.id),
            "fgColor": QColor("white"),
            "bgColor": QColor("red"),
        }

    def test_init(self, ddb):
        gp = f_groupeMatiere()
        an = f_annee()
        a = ddb.Matiere(
            nom="bla", groupe=gp.id, _fgColor=4294967295, _bgColor=4294901760,
        )
        b = ddb.Matiere(nom="bla", groupe=gp.id)

        # default value
        assert b._fgColor == QColor("black").rgba()
        assert b._bgColor == QColor("white").rgba()

        # from QColor
        c = ddb.Matiere(nom="bla", groupe=gp.id, bgColor=QColor("red"))
        assert c._bgColor == 4294901760
        d = ddb.Matiere(nom="bla", groupe=gp.id, fgColor=QColor("blue"))
        assert d._fgColor == 4278190335

        # property
        c.bgColor = QColor("blue")
        assert c._bgColor == 4278190335
        assert c.bgColor == QColor("blue")
        c.fgColor = QColor("red")
        assert c._fgColor == 4294901760
        assert c.fgColor == QColor("red")

        # Qcolorsetter
        c.bgColor = "blue"
        assert c._bgColor == 4278190335
        c.bgColor = (123, 3, 134)
        assert QColor(c._bgColor) == QColor(123, 3, 134)

    def test_delete_mixin_position(self, reset_db):
        a = f_matiere()
        b = f_matiere(groupe=a.groupe)
        with db_session:
            assert Matiere[a.id].position == 0
            assert Matiere[b.id].position == 1
            Matiere[a.id].delete()
        with db_session:
            assert Matiere[b.id].position == 0

            # a.before_delete_position = Ma

    def test_color_mixin(self, reset_db):
        a = f_groupeMatiere()
        with db_session:
            z = Matiere(nom="bk", groupe=a.id)
            b = Matiere(nom="bk", groupe=a.id, fgColor="red")
            c = Matiere(nom="bk", groupe=a.id, bgColor="green")
        with db_session:
            assert Matiere[z.id].bgColor == QColor("white")
            assert Matiere[z.id].fgColor == QColor("black")
            assert Matiere[b.id].bgColor == QColor("white")
            assert Matiere[b.id].fgColor == QColor("red")
            assert Matiere[c.id].bgColor == QColor("green")
            assert Matiere[c.id].fgColor == QColor("black")
            assert Matiere[b.id].to_dict()["fgColor"] == QColor("red")
            assert Matiere[c.id].to_dict()["bgColor"] == QColor("green")

    def test_page_par_section(self, ddbr):
        m = f_matiere(nom="Math", _bgColor=4294967295, _fgColor=4294901760)
        un = f_activite(nom="un", matiere=m.id)
        deux = f_activite(nom="deux", matiere=m.id)
        trois = f_activite()
        w = b_page(3, activite=deux, titre="pagedeux", created=datetime(1212, 12, 12))
        x = b_page(3, activite=un, titre="pageun", created=datetime(1111, 11, 11))
        # y = b_page(3, activite=trois, titre="âge")

        with db_session:
            assert Matiere[m.id].pages_par_section() == [
                {
                    "id": str(un.id),
                    "nom": "un",
                    "matiere": str(m.id),
                    "pages": [
                        {
                            "activite": str(un.id),
                            "created": "1111-11-11T00:00:00",
                            "id": str(x[0].id),
                            "matiereNom": "Math",
                            "lastPosition": None,
                            "matiere": str(m.id),
                            "matiereBgColor": QColor("white"),
                            "matiereFgColor": QColor("red"),
                            "modified": "1111-11-11T00:00:00",
                            "titre": "pageun",
                        },
                        {
                            "activite": str(un.id),
                            "created": "1111-11-11T00:00:00",
                            "id": str(x[1].id),
                            "lastPosition": None,
                            "matiere": str(m.id),
                            "matiereNom": "Math",
                            "matiereBgColor": QColor("white"),
                            "matiereFgColor": QColor("red"),
                            "modified": "1111-11-11T00:00:00",
                            "titre": "pageun",
                        },
                        {
                            "activite": str(un.id),
                            "created": "1111-11-11T00:00:00",
                            "id": str(x[2].id),
                            "lastPosition": None,
                            "matiere": str(m.id),
                            "matiereNom": "Math",
                            "matiereBgColor": QColor("white"),
                            "matiereFgColor": QColor("red"),
                            "modified": "1111-11-11T00:00:00",
                            "titre": "pageun",
                        },
                    ],
                    "position": 0,
                },
                {
                    "id": str(deux.id),
                    "nom": "deux",
                    "matiere": str(m.id),
                    "pages": [
                        {
                            "activite": str(deux.id),
                            "created": "1212-12-12T00:00:00",
                            "id": str(w[0].id),
                            "lastPosition": None,
                            "matiere": str(m.id),
                            "matiereNom": "Math",
                            "matiereBgColor": QColor("white"),
                            "matiereFgColor": QColor("red"),
                            "modified": "1212-12-12T00:00:00",
                            "titre": "pagedeux",
                        },
                        {
                            "activite": str(deux.id),
                            "created": "1212-12-12T00:00:00",
                            "id": str(w[1].id),
                            "lastPosition": None,
                            "matiere": str(m.id),
                            "matiereNom": "Math",
                            "matiereBgColor": QColor("white"),
                            "matiereFgColor": QColor("red"),
                            "modified": "1212-12-12T00:00:00",
                            "titre": "pagedeux",
                        },
                        {
                            "activite": str(deux.id),
                            "created": "1212-12-12T00:00:00",
                            "id": str(w[2].id),
                            "lastPosition": None,
                            "matiere": str(m.id),
                            "matiereNom": "Math",
                            "matiereBgColor": QColor("white"),
                            "matiereFgColor": QColor("red"),
                            "modified": "1212-12-12T00:00:00",
                            "titre": "pagedeux",
                        },
                    ],
                    "position": 1,
                },
            ]  # pages = [
        #     {
        #         "created": "2019-03-14T17:35:58.111997",
        #         "modified": "2019-03-14T17:35:58.111997",
        #         "titre": "quoi amener défendre charger seulement",
        #         "activite": str,
        #         "lastPosition": None,
        #     },
        #     {
        #         "created": "2019-10-30T10:54:18.834326",
        #         "modified": "2019-10-30T10:54:18.834326",
        #         "titre": "sujet grandir emporter monter rencontrer",
        #         "activite": deux.id,
        #         "lastPosition": None,
        #     },
        #     {
        #         "created": "2019-08-17T21:33:55.644158",
        #         "modified": "2019-08-17T21:33:55.644158",
        #         "titre": "oreille blague soleil poursuivre riche",
        #         "activite": trois.id,
        #         "lastPosition": None,
        #     },
        #     {
        #         "created": "2020-02-18T22:25:14.288186",
        #         "modified": "2020-02-18T22:25:14.288186",
        #         "titre": "enfer cette simple ensemble rendre",
        #         "activite": 3,
        #         "lastPosition": None,
        #     },
        #     {
        #         "created": "2019-09-16T03:57:38.860509",
        #         "modified": "2019-09-16T03:57:38.860509",
        #         "titre": "grand-père monde cœur reposer rappeler",
        #         "activite": 1,
        #         "lastPosition": None,
        #     },
        # ]
        # with db_session:
        #     for p in pages:
        #         ddbr.Page(**p)
        # with db_session:
        #     mm = ddbr.Matiere[m.id]
        #     q = mm.pages_par_section()
        #     assert q == [
        #         {
        #             "id": 1,
        #             "matiere": m.id,
        #             "nom": "un",
        #             "pages": [
        #                 {
        #                     "activite": 1,
        #                     "created": "2019-09-16T03:57:38.860509",
        #                     "id": 5,
        #                     "lastPosition": None,
        #                     "matiere": m.id,
        #                     "matiereNom": "Math",
        #                     "modified": "2019-09-16T03:57:38.860509",
        #                     "titre": "grand-père monde cœur reposer rappeler",
        #                     "matiereBgColor": QColor("white"),
        #                     "matiereFgColor": QColor("red"),
        #                 },
        #                 {
        #                     "activite": 1,
        #                     "created": "2019-08-17T21:33:55.644158",
        #                     "id": 3,
        #                     "lastPosition": None,
        #                     "matiere": m.id,
        #                     "matiereNom": "Math",
        #                     "modified": "2019-08-17T21:33:55.644158",
        #                     "titre": "oreille blague soleil poursuivre riche",
        #                     "matiereBgColor": QColor("white"),
        #                     "matiereFgColor": QColor("red"),
        #                 },
        #                 {
        #                     "activite": 1,
        #                     "created": "2019-03-14T17:35:58.111997",
        #                     "id": 1,
        #                     "lastPosition": None,
        #                     "matiere": m.id,
        #                     "matiereNom": "Math",
        #                     "modified": "2019-03-14T17:35:58.111997",
        #                     "titre": "quoi amener défendre charger seulement",
        #                     "matiereBgColor": QColor("white"),
        #                     "matiereFgColor": QColor("red"),
        #                 },
        #             ],
        #             "position": 0,
        #         },
        #         {"id": 2, "matiere": m.id, "nom": "deux", "pages": [], "position": 1},
        #         {
        #             "id": 3,
        #             "matiere": m.id,
        #             "nom": "trois",
        #             "position": 2,
        #             "pages": [
        #                 {
        #                     "activite": 3,
        #                     "created": "2020-02-18T22:25:14.288186",
        #                     "id": 4,
        #                     "lastPosition": None,
        #                     "matiere": m.id,
        #                     "matiereNom": "Math",
        #                     "modified": "2020-02-18T22:25:14.288186",
        #                     "titre": "enfer cette simple ensemble rendre",
        #                     "matiereBgColor": QColor("white"),
        #                     "matiereFgColor": QColor("red"),
        #                 },
        #                 {
        #                     "activite": 3,
        #                     "created": "2019-10-30T10:54:18.834326",
        #                     "id": 2,
        #                     "lastPosition": None,
        #                     "matiere": m.id,
        #                     "matiereNom": "Math",
        #                     "modified": "2019-10-30T10:54:18.834326",
        #                     "titre": "sujet grandir emporter monter rencontrer",
        #                     "matiereBgColor": QColor("white"),
        #                     "matiereFgColor": QColor("red"),
        #                 },
        #             ],
        #         },
        #     ]


class TestActivite:
    def test_delete_mixin_position(self, reset_db):
        a = b_activite(2)
        with db_session:
            assert Activite[a[0].id].position == 0
            assert Activite[a[1].id].position == 1
            Activite[a[0].id].delete()
        with db_session:
            assert Activite[a[1].id].position == 0


class TestSection:
    def test_init(self, ddbr):
        p = f_page()
        f_section(page=p.id)
        with db_session:
            s = ddbr.Section(page=p.id)
        with db_session:
            x = ddbr.Section(page=p.id)
        assert s._position == 1
        assert x._position == 2
        with db_session:
            z = ddbr.Section(page=p.id, position=1)
            assert ddbr.Section[s.id].position == 2
            assert ddbr.Section[x.id].position == 3

    def test_get_with_string(self, ddbr):
        x = f_section()
        strid = str(x.id)
        with db_session:
            z = Section[strid]

    def test_delete_mixin_position(self, reset_db):
        a = f_page()
        x = f_section(page=a.id)
        y = f_section(page=a.id)
        with db_session:
            assert Section[x.id].position == 0
            assert Section[y.id].position == 1
            Section[x.id].delete()
        with db_session:
            assert Section[y.id].position == 0

    def test_position_property(self, ddb):
        p = f_page()
        with db_session:
            z = f_section(page=p.id)
            flush()
            x = f_section(page=p.id)
            flush()
            assert z.position == 0
            assert x.position == 1
            x.position = 0
            assert z.position == 1
            assert x.position == 0

    def test_inheritance_position(self, reset_db):
        page = f_page()
        f_section(page=page.id)
        with db_session:
            s = TextSection(page=page.id)
            t = EquationSection(page=page.id)
            u = Section(page=page.id)
            assert s.position == 1
            assert t.position == 2
            assert u.position == 3

    def test_inheritance_position2(self, reset_db):
        page = f_page()
        r = f_section(page=page.id)
        with db_session:
            s = TextSection(page=page.id)
        with db_session:
            t = EquationSection(page=page.id)
        with db_session:
            u = Section(page=page.id)
        with db_session:
            assert Section[r.id].position == 0
            assert Section[s.id].position == 1
            assert Section[t.id].position == 2
            assert Section[u.id].position == 3

    def test_to_dict(self, ddbr):
        a = datetime.utcnow()
        x = f_section(created=a, td=True)
        assert x["created"] == a.isoformat()
        assert x["modified"] == a.isoformat()

    def test_before_insert_no_position(self, ddb):
        """"remember factory are flushed"""
        a = f_page()
        b = f_section(page=a.id)
        flush()
        assert b.position == 0
        c = f_section(page=a.id)
        flush()
        assert b.position == 0
        assert c.position == 1

    def test_before_insert_position_to_high(self, ddb):
        a = f_page()
        b = f_section(page=a.id)
        flush()
        assert b.position == 0
        c = f_section(page=a.id, position=3)
        flush()
        assert b.position == 0
        assert c.position == 1

    def test_update_position(self, ddb):
        a = f_page()
        b = b_section(5, page=a.id)
        modified_item = b[0].modified
        flush()
        c = f_section(page=a.id, position=3)
        flush()
        # test new item
        assert c.position == 3

        # position n'influence pas la date de modif de section
        assert a.content[0].modified == modified_item

        # inflence l date de modif de page
        page_modified = a.modified
        wait()
        f_section(page=a.id, created=datetime.utcnow())
        assert page_modified < a.modified

    def test_before_update(self, reset_db):
        with db_session:
            a = make_proxy(f_section())
            b = a.modified
        with db_session:
            a.created = datetime.utcnow()
        with db_session:
            assert a.modified > b
            assert a.page.modified == a.modified

    def test_before_insert(self, ddbr):
        avant = datetime.utcnow()
        wait()
        s = f_section(created=datetime.utcnow())
        wait()
        apres = datetime.utcnow()
        assert avant < s.created < apres
        assert s.created == s.modified
        with db_session:
            assert ddbr.Page[s.page.id].modified >= s.modified

    def test_update_position__and_time_on_delete(self, ddbr):
        p = f_page()
        s0 = f_section(page=p.id)
        s1 = f_section(page=p.id)
        s2 = f_section(page=p.id)

        with db_session:
            now = ddbr.Page[p.id].modified
            wait()
            ddbr.Section[s0.id].delete()

        with db_session:
            # resultat avec décalage
            assert ddbr.Section[s1.id].position == 0
            assert ddbr.Section[s2.id].position == 1
            # page mis à jour
            assert now < ddbr.Page[p.id].modified

    @pytest.mark.parametrize(
        "start, new_pos, poses", [(2, 3, (0, 1, 3, 2, 4)), (3, 1, (0, 2, 3, 1, 4)),]
    )
    def test_update_position_change_position_descend(self, ddbr, start, new_pos, poses):
        a = f_page()
        secs = []
        with db_session:
            for i in range(5):
                z = ddbr.Section(page=a.id, position=i)
                flush()
                secs.append(z)
            for i, e in enumerate(secs):
                assert e.position == i
        with db_session:
            x = ddbr.Section[secs[start].id]
            x.position = new_pos
        with db_session:
            for index, value in enumerate(poses):
                assert ddbr.Section[secs[index].id].position == value


class TestImageSection:
    def test_factory(self):
        a = f_imageSection(path="mon/path")
        assert a.path == "mon/path"

    def test_to_dict(self):
        a = f_imageSection(path="mon/path", td=True)
        assert a["path"] == "mon/path"
        assert a["annotations"] == []


class TestTextSection:
    def test_factory(self):
        assert f_textSection(text="bla").text == "bla"

    def test_default_is_empty_string(self, ddb):
        p = f_page()
        tex = ddb.TextSection(page=p.id)
        assert tex.text == "<body></body>"


class TestTableDataSection:
    def test_datas(self, ddb):
        p = f_page()
        a = ddb.TableDataSection(
            _datas='["", "", "", "", "", ""]', rows=3, columns=2, page=p.id
        )
        assert a.datas == ["", "", "", "", "", ""]

    def test_update_datas(self, ddb):
        p = f_page()
        a = ddb.TableDataSection(
            _datas='["", "", "", "", "", ""]', rows=3, columns=2, page=p.id
        )
        a.update_datas(4, "g")
        assert a.datas == ["", "", "", "", "g", ""]

    def test_to_dict(self, ddb):
        p = f_page()
        a = ddb.TableDataSection(
            _datas='["", "", "", "", "", ""]', rows=3, columns=2, page=p.id
        )
        assert a.to_dict() == {
            "classtype": "TableDataSection",
            "columns": 2,
            "created": a.created.isoformat(),
            "datas": ["", "", "", "", "", ""],
            "id": str(a.id),
            "modified": a.modified.isoformat(),
            "page": str(p.id),
            "position": 0,
            "rows": 3,
        }


class TestOperationSection:
    def test_init(self, ddb):
        x = f_page()
        # normal
        a = ddb.OperationSection(string="1+2", page=x.id)
        assert a._datas == '["", "", "", "1", "+", "2", "", ""]'
        assert a.datas == ["", "", "", "1", "+", "2", "", ""]
        assert a.rows == 4
        assert a.columns == 2

    def test_error_in_init(self, ddb):
        with pytest.raises(MyCartableOperationError) as err:
            ddb.OperationSection(string="1(2")
        assert str(err.value) == "1(2 est une entrée invalide"

    def test_datas(self, ddb):
        f_page()

        # do not use content if None
        with pytest.raises(TypeError):
            a = ddb.OperationSection(page=1)

    def test_to_dict(self, reset_db):
        item = f_additionSection(string="259+135")
        assert item.to_dict() == {
            "classtype": "AdditionSection",
            "created": item.created.isoformat(),
            "rows": 4,
            "columns": 4,
            "datas": [
                "",
                "",
                "",
                "",
                "",
                "2",
                "5",
                "9",
                "+",
                "1",
                "3",
                "5",
                "",
                "",
                "",
                "",
            ],
            "id": str(item.id),
            "modified": item.modified.isoformat(),
            "page": str(item.page.id),
            "position": 0,
            "size": 16,
            "virgule": 0,
        }

    def test_update_datas(self, ddbr: Database):
        item = f_additionSection(string="259+135")
        with db_session:
            ddbr.Section[item.id].update_datas(15, 4)

        with db_session:
            assert ddbr.Section[item.id].datas[15] == 4


class TestAddditionSection:
    def test_factory(self):
        assert f_additionSection(string="15+3").datas == [
            "",
            "",
            "",
            "",
            "1",
            "5",
            "+",
            "",
            "3",
            "",
            "",
            "",
        ]

        f_additionSection()

    @pytest.mark.parametrize(
        "string, res",
        [
            ("9+8", {1, 10, 11}),
            ("1+2", {7}),
            ("345+289", {1, 2, 13, 14, 15}),
            ("1+2+3", {9}),
            ("1,1+1", {1, 13, 15}),
        ],
    )
    def test_get_editables(self, ddb, string, res):
        x = f_additionSection(string=string)
        assert x.get_editables() == res


class TestSoustractionSection:
    def test_factory(self):
        res = (
            ["", "", "1", "", "", "5", "", "-", "",]
            + ["", "", "", "3", "", "", "", "",]
            + ["", "", "", "",]
        )
        assert f_soustractionSection(string="15-3").datas == res

        f_soustractionSection()

    def test_lines(self, ddb):
        a = f_soustractionSection(string="24-13")
        # ['', '', '2', '', '', '4', '', '-', '', '1', '', '', '3', '', '', '', '', '', '', '', ''] 7 3
        assert a.line_0 == ["", "", "2", "", "", "4", ""]
        assert a.line_1 == [
            "-",
            "",
            "1",
            "",
            "",
            "3",
            "",
        ]
        assert a.line_2 == [""] * a.columns

    @pytest.mark.parametrize(
        "string, res",
        [
            ("9-8", {10}),
            ("22-2", {16, 19}),
            ("22-21", {16, 19}),
            ("345-28", {22, 25, 28}),
            ("345-285", {22, 25, 28}),
            ("2,2-1,1", {18, 22}),
        ],
    )
    def test_get_editables(self, ddb, string, res):
        x = f_soustractionSection(string=string)
        assert x.get_editables() == res


class TestMultiplicationSection:
    def test_factory(self):
        assert f_multiplicationSection(string="1*2").datas == [
            "",
            "",
            "",
            "2",
            "x",
            "1",
            "",
            "",
        ]

        f_multiplicationSection()

    def test_properties(self, ddb):
        a = f_multiplicationSection(string="12*34")
        assert a.n_chiffres == 2
        assert a.line_0 == ["", "", "3", "4"]
        assert a.line_1 == ["x", "", "1", "2"]

        a._datas = '["", "", "", "", "", "", "", "", "", "", "1", "2", "x", "", "3", "4", "", "", "", "", "", "", "", "", "", "", "", "", "f", "", "", "z"]'
        assert a.line_res == ["f", "", "", "z"]

    @pytest.mark.parametrize(
        "string, res",
        [
            ("2*1", {7}),
            ("2*5", {1, 10, 11}),
            ("22*5", {1, 2, 13, 14, 15}),
            (
                "22*55",
                {3, 8, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39},
            ),
            ("2,2*5,5", {3, 9} | set(range(25, 48)) - set(range(24, 48, 6)),),
            (
                "325,12*99,153",
                set(
                    itertools.chain.from_iterable(
                        range(x, 60, 12) for x in [6, 7, 8, 10]
                    )
                )
                | set(range(84, 168)) - set(range(84, 168, 12)),
            ),
        ],
    )
    def test_get_editables(self, ddb, string, res):
        x = f_multiplicationSection(string=string)
        assert x.get_editables() == res


class TestDivisionSection:
    def test_factory(self, ddb):
        x = f_divisionSection(string="34/3")
        assert x.dividende == "34"
        assert x.diviseur == "3"

    def test_is_ligne_dividende(self):
        tm = f_divisionSection("264/11")
        check_is_range(tm, "is_ligne_dividende", range(9))

    def test_is_ligne_last(self):
        tm = f_divisionSection("264/11")
        check_is_range(tm, "is_ligne_last", range(36, 45))

    @pytest.mark.parametrize(
        "string, res",
        [
            # ("5/4", set(range(84)) - {1}),
            ("264/11", {10, 13, 16, 19, 22, 25} | {28, 31, 34, 37, 40, 43},),
        ],
    )
    def test_get_editables(self, string, res):
        x = f_divisionSection(string=string)
        assert x.get_editables() == res

    #     # 'rows': 5, 'columns': 9, '
    #
    #     # '', 'X', '',  '*', 'Y', '', '*', 'Z', '' //8
    #     # '', '*', '*', '',  '*', '*', '', '*', '', // 17
    #     # '', '*', '', '*',  '*', '', '*', '*', '', // 26
    #     # '', '*', '*', '',  '*', '*', '', '*', '', // 35
    #     # '', '*', '', '',   '*', '',  '', '*', '' , //44

    def test_to_dict(self, reset_db):
        x = f_divisionSection(string="5/4")
        assert x.to_dict() == {
            "classtype": "DivisionSection",
            "columns": 12,
            "datas": ["", "5"] + [""] * 82,
            "dividende": "5",
            "diviseur": "4",
            "id": str(x.id),
            "page": str(x.page.id),
            "created": x.created.isoformat(),
            "modified": x.modified.isoformat(),
            "position": 0,
            "quotient": "",
            "rows": 7,
            "size": 84,
            "virgule": 0,
        }

    def test_as_num(self):
        x = f_divisionSection(string="5/4")
        assert x.diviseur_as_num == 4
        assert x.dividende_as_num == 5

        x = f_divisionSection(string="5,333333/4,1")
        assert x.diviseur_as_num == 4.1
        assert x.dividende_as_num == 5.333333


class TestAnnotations:
    def test_init(self, ddb):
        s = f_section()
        x = ddb.Annotation(x=0.1, y=0.4, section=s.id)
        x.style.flush()
        assert isinstance(x.style.styleId, UUID)

    def test_factory(self, ddbr):
        a = f_annotation()
        assert isinstance(a.id, uuid.UUID)

    def test_init_and_to_dict(self, ddb):
        s = f_section()
        x = ddb.Annotation(x=0.1, y=0.4, section=s.id, style={"bgColor": "red"})
        assert x.style.bgColor == QColor("red")

        r = x.to_dict()
        assert r["x"] == 0.1
        assert r["y"] == 0.4
        assert r["section"] == Section[s.id]
        assert r["bgColor"] == QColor("red")
        assert r["fgColor"] == QColor("black")
        assert r["id"] == str(x.id)

    def test_set(self, ddbr):
        x = f_annotation(x=0.3)
        with db_session:
            x = Annotation[x.id]
            assert not x.style.underline
            x.set(**{"x": 0.7, "style": {"underline": True}, "attrs": {"y": "0.234"}})
            assert x.x == 0.7
            assert x.style.underline
            assert x.y == 0.234
            x.set(**{"x": 0.9})
            assert x.x == 0.9

    def test_add_modify_section_and_page_modified_attribute(self, ddbr):
        p = f_page()
        before_p = p.modified
        s = f_section(page=p.id, created=datetime.utcnow())
        before = s.modified

        wait()
        a = f_annotation(section=s.id)

        with db_session:
            n = ddbr.Section[s.id]
            after = n.modified
            wait()
            after_p = n.page.modified

        assert before < after
        assert before_p < after_p

    #
    def test_delete_modify_section_and_page_modified_attribute(self, ddbr):
        p = f_page()
        s = f_section(page=p.id, created=datetime.utcnow())
        a = f_annotation(section=s.id)
        wait()
        with db_session:
            n = ddbr.Section[s.id]
            before = n.modified
            before_p = n.page.modified
        wait()
        with db_session:
            ddbr.Annotation[a.id].delete()

        with db_session:
            n = ddbr.Section[s.id]
            after = n.modified
            after_p = n.page.modified

        assert before < after
        assert before_p < after_p

    def test_delete_not_fail_if_section_deleted(self, ddbr):
        a = f_annotation()
        with db_session:
            s = ddbr.Section[a.section.id]
            a = ddbr.Annotation[a.id]
            s.delete()
            a.delete()

    def test_annotation_text(self):
        an = f_annotationText(text=" jihkujgy ")
        assert an.text == " jihkujgy "

    def test_annotation_dessin(self):
        an = f_annotationText(text=" jihkujgy ")
        assert an.text == " jihkujgy "

    def test_annotation_dession(self):
        an = f_annotationDessin()

    def test_getitem(self, reset_db):
        f_annotation()
        f_annotationDessin()
        f_annotationText()

        with db_session:
            annots = Annotation.select()[:]
            a = annots[0].as_type()
            assert isinstance(a, Annotation)
            a = annots[1].as_type()
            assert isinstance(a, AnnotationDessin)
            a = annots[2].as_type()
            assert isinstance(a, AnnotationText)


class TestTableauSection:
    def test_init(self, ddb):
        x = f_page()
        # normal
        a = ddb.TableauSection(lignes=3, colonnes=4, page=x.id)
        a.flush()
        assert a.cells.count() == 12
        # si pas d'erreur c que pq ok
        assert [ddb.TableauCell[a.id, y, x] for y in range(3) for x in range(4)]

        b = f_tableauSection()

    @pytest.mark.parametrize(
        "modele, zero_0, zero_1, un_0, un_1",
        [
            (
                "ligne0",
                QColor("blue").lighter(),
                QColor("blue").lighter(),
                QColor("transparent"),
                QColor("transparent"),
            ),
            (
                "colonne0",
                QColor("gray").lighter(),
                QColor("transparent"),
                QColor("gray").lighter(),
                QColor("transparent"),
            ),
            (
                "ligne0-colonne0",
                QColor("blue").lighter(),
                QColor("blue").lighter(),
                QColor("gray").lighter(),
                QColor("transparent"),
            ),
            (
                "",
                QColor("transparent"),
                QColor("transparent"),
                QColor("transparent"),
                QColor("transparent"),
            ),
        ],
    )
    def test_init_with_model(self, ddbr, modele, zero_0, zero_1, un_0, un_1):
        x = f_tableauSection(2, 2, modele)
        with db_session:
            a = TableauSection[x.id]
            assert TableauCell[a, 0, 0].style.bgColor.rgba() == zero_0.rgba()
            assert TableauCell[a, 0, 1].style.bgColor.rgba() == zero_1.rgba()
            assert TableauCell[a, 1, 0].style.bgColor.rgba() == un_0.rgba()
            assert TableauCell[a, 1, 1].style.bgColor.rgba() == un_1.rgba()

    def test_to_dict(self, ddb):
        item = f_tableauSection(lignes=3, colonnes=4)

        assert item.to_dict() == {
            "classtype": "TableauSection",
            "created": item.created.isoformat(),
            "lignes": 3,
            "colonnes": 4,
            "id": str(item.id),
            "modified": item.modified.isoformat(),
            "page": str(item.page.id),
            "position": 0,
        }

    def test_get_par_ligne(self, ddb):
        t = f_tableauSection(lignes=5, colonnes=4)
        p1 = t.get_cells_par_ligne(0)
        assert len(p1) == 4
        assert p1 == [
            TableauCell[TableauSection[t.id], 0, 0],
            TableauCell[TableauSection[t.id], 0, 1],
            TableauCell[TableauSection[t.id], 0, 2],
            TableauCell[TableauSection[t.id], 0, 3],
        ]
        p1 = t.get_cells_par_ligne(1)
        assert len(p1) == 4
        assert p1 == [
            TableauCell[TableauSection[t.id], 1, 0],
            TableauCell[TableauSection[t.id], 1, 1],
            TableauCell[TableauSection[t.id], 1, 2],
            TableauCell[TableauSection[t.id], 1, 3],
        ]

        p1 = t.get_cells_par_ligne(2)
        assert len(p1) == 4
        assert p1 == [
            TableauCell[TableauSection[t.id], 2, 0],
            TableauCell[TableauSection[t.id], 2, 1],
            TableauCell[TableauSection[t.id], 2, 2],
            TableauCell[TableauSection[t.id], 2, 3],
        ]
        p1 = t.get_cells_par_ligne(3)
        assert len(p1) == 4
        assert p1 == [
            TableauCell[TableauSection[t.id], 3, 0],
            TableauCell[TableauSection[t.id], 3, 1],
            TableauCell[TableauSection[t.id], 3, 2],
            TableauCell[TableauSection[t.id], 3, 3],
        ]
        p1 = t.get_cells_par_ligne(4)
        assert len(p1) == 4
        assert p1 == [
            TableauCell[TableauSection[t.id], 4, 0],
            TableauCell[TableauSection[t.id], 4, 1],
            TableauCell[TableauSection[t.id], 4, 2],
            TableauCell[TableauSection[t.id], 4, 3],
        ]

    @staticmethod
    def peupler_tableau_manipulation():
        with db_session:
            a = f_tableauSection(3, 4)  # premiere colone : 0,4,8
            cells = a.get_cells()[:]
            cells[0].texte = "0_0"
            cells[0].style.underline = True
            cells[4].texte = "1_0"
            cells[4].style.bgColor = "yellow"
            cells[8].texte = "2_0"
            cells[8].style.fgColor = "blue"
            cells = [x.to_dict(exclude=["x", "y"]) for x in cells]
            [x["style"].pop("styleId") for x in cells]
            return make_proxy(a), cells

    def test_insert_one_line(self, ddbr):
        a, cells = self.peupler_tableau_manipulation()
        with db_session:
            a.insert_one_line(1)
        with db_session:
            assert a.cells.count() == 16
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[8] == cells[4]
            assert cells_after[12] == cells[8]
            assert cells_after[4]["texte"] == ""
            assert cells_after[4]["style"]["underline"] == False

    def test_insert_one_line_start(self, ddbr):
        a, cells = self.peupler_tableau_manipulation()
        with db_session:
            a.insert_one_line(0)
        with db_session:
            assert a.cells.count() == 16
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[4] == cells[0]
            assert cells_after[8] == cells[4]
            assert cells_after[12] == cells[8]
            assert cells_after[0]["texte"] == ""
            assert cells_after[0]["style"]["underline"] == False

    def test_insert_one_avant_line_dernier(self, ddbr):
        a, cells = self.peupler_tableau_manipulation()
        with db_session:
            a.insert_one_line(2)
        with db_session:
            assert a.cells.count() == 16
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[4] == cells[4]
            assert cells_after[12] == cells[8]
            assert cells_after[8]["texte"] == ""
            assert cells_after[8]["style"]["underline"] == False

    def test_insert_one_apres_dernier(self, ddbr):
        a, cells = self.peupler_tableau_manipulation()
        with db_session:
            a.insert_one_line(3)
        with db_session:
            assert a.cells.count() == 16
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[4] == cells[4]
            assert cells_after[8] == cells[8]
            assert cells_after[12]["texte"] == ""
            assert cells_after[12]["style"]["underline"] == False

    def test_insert_append_one_line(self, ddbr):
        a, cells = self.peupler_tableau_manipulation()
        with db_session:
            a.append_one_line()
        with db_session:
            assert a.cells.count() == 16
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[4] == cells[4]
            assert cells_after[8] == cells[8]
            assert cells_after[12]["texte"] == ""
            assert cells_after[12]["style"]["underline"] == False

    def test_remove_line_middle(self, ddbr):
        a, cells = self.peupler_tableau_manipulation()
        with db_session:
            a.remove_on_line(1)
        with db_session:
            assert a.cells.count() == 8
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[4] == cells[8]

    def test_remove_line_last(self, ddbr):
        a, cells = self.peupler_tableau_manipulation()
        with db_session:
            a.remove_one_line(2)
        with db_session:
            assert a.cells.count() == 8
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[4] == cells[4]

    def test_remove_line_middle(self, ddbr):
        a, cells = self.peupler_tableau_manipulation()
        with db_session:
            a.remove_one_line(0)
        with db_session:
            assert a.cells.count() == 8
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[4]
            assert cells_after[4] == cells[8]

    @staticmethod
    def peupler_tableau_manip_colonnes():
        with db_session:
            a = f_tableauSection(3, 4)
            cells = a.get_cells()[:]
            cells[0].texte = "0_0"
            cells[0].style.underline = True
            cells[1].texte = "0_1"
            cells[1].style.bgColor = "yellow"
            cells[2].texte = "0_2"
            cells[2].style.fgColor = "blue"
            cells[3].texte = "0_3"
            cells[3].style.strikeout = True
            cells = [x.to_dict(exclude=["x", "y"]) for x in cells]
            [x["style"].pop("styleId") for x in cells]
            return make_proxy(a), cells

    def test_insert_one_col_middle(self, ddbr):
        a, cells = self.peupler_tableau_manip_colonnes()
        with db_session:
            a.insert_one_column(1)
        with db_session:
            assert a.cells.count() == 15
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[2] == cells[1]
            assert cells_after[3] == cells[2]
            assert cells_after[4] == cells[3]
            assert cells_after[1]["texte"] == ""
            assert cells_after[1]["style"]["bgColor"] == QColor("transparent")

    def test_insert_one_col_start(self, ddbr):
        a, cells = self.peupler_tableau_manip_colonnes()
        with db_session:
            a.insert_one_column(0)
        with db_session:
            assert a.cells.count() == 15
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[1] == cells[0]
            assert cells_after[2] == cells[1]
            assert cells_after[3] == cells[2]
            assert cells_after[4] == cells[3]
            assert cells_after[0]["texte"] == ""
            assert cells_after[0]["style"]["bgColor"] == QColor("transparent")

    def test_insert_one_col_avant_dernier(self, ddbr):
        a, cells = self.peupler_tableau_manip_colonnes()
        with db_session:
            a.insert_one_column(3)
        with db_session:
            assert a.cells.count() == 15
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[1] == cells[1]
            assert cells_after[2] == cells[2]
            assert cells_after[4] == cells[3]
            assert cells_after[3]["texte"] == ""
            assert cells_after[3]["style"]["bgColor"] == QColor("transparent")

    def test_insert_one_col__dernier(self, ddbr):
        a, cells = self.peupler_tableau_manip_colonnes()
        with db_session:
            a.insert_one_column(4)
        with db_session:
            assert a.cells.count() == 15
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[1] == cells[1]
            assert cells_after[2] == cells[2]
            assert cells_after[3] == cells[3]
            assert cells_after[4]["texte"] == ""
            assert cells_after[4]["style"]["bgColor"] == QColor("transparent")

    def test_insert_append_colonne(self, ddbr):
        a, cells = self.peupler_tableau_manip_colonnes()
        with db_session:
            a.append_one_column()
        with db_session:
            assert a.cells.count() == 15
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[1] == cells[1]
            assert cells_after[2] == cells[2]
            assert cells_after[3] == cells[3]
            assert cells_after[4]["texte"] == ""
            assert cells_after[4]["style"]["bgColor"] == QColor("transparent")

    def test_remove_one_col_middle(self, ddbr):
        a, cells = self.peupler_tableau_manip_colonnes()
        with db_session:
            a.remove_one_column(2)
        with db_session:
            assert a.cells.count() == 9
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[1] == cells[1]
            assert cells_after[2] == cells[3]

    def test_remove_one_col_start(self, ddbr):
        a, cells = self.peupler_tableau_manip_colonnes()
        with db_session:
            a.remove_one_column(0)
        with db_session:
            assert a.cells.count() == 9
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[1]
            assert cells_after[1] == cells[2]
            assert cells_after[2] == cells[3]

    def test_remove_one_col_end(self, ddbr):
        a, cells = self.peupler_tableau_manip_colonnes()
        with db_session:
            a.remove_one_column(3)
        with db_session:
            assert a.cells.count() == 9
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[1] == cells[1]
            assert cells_after[2] == cells[2]


class TestTableauCell:
    def test_init(self, ddb):
        # simple
        t = f_tableauSection(lignes=0)
        a = ddb.TableauCell(tableau=t, x=0, y=0)
        assert a.x == 0
        assert a.y == 0
        assert a.style.bgColor == QColor("transparent")
        assert ddb.TableauCell[a.tableau, 0, 0] == a
        b = ddb.TableauCell(tableau=t, x=0, y=1, style={"bgColor": "red"})
        assert b.style._bgColor == 4294901760

    def test_factory(self, reset_db):
        t = f_tableauSection(lignes=0, colonnes=0)
        f_tableauCell(tableau=t.id)
        f_tableauCell(x=1, tableau=t.id)

    def test_to_dict(self, reset_db):
        s = f_style(bgColor="red")
        b = f_tableauCell(x=2, y=0, style=s.styleId, texte="bla")
        with db_session:
            assert b.to_dict() == {
                "tableau": str(b.tableau.id),
                "x": 2,
                "y": 0,
                "texte": "bla",
                "style": {
                    "bgColor": QColor("red"),
                    "family": "",
                    "fgColor": QColor("black"),
                    "styleId": str(s.styleId),
                    "pointSize": None,
                    "strikeout": False,
                    "underline": False,
                    "weight": None,
                },
            }

    def test_set(self, ddbr):
        x = f_tableauCell(texte="bla")
        with db_session:
            x = TableauCell[x.tableau.id, 0, 0]
            assert not x.style.underline
            x.set(**{"texte": "bbb"})
            assert x.texte == "bbb"
            x.set(**{"texte": "aaa", "style": {"underline": True}})
            assert x.texte == "aaa"
            assert x.style.underline


class TestStyle:
    def test_init(self, ddb):
        # set tout
        item = Style(
            fgColor="red",
            bgColor="blue",
            family="Verdana",
            underline=True,
            pointSize=1.5,
            strikeout=True,
            weight=QFont.DemiBold,
        )
        assert item.fgColor == QColor("red")
        assert item.bgColor == QColor("blue")
        # uniquement par défault
        item = Style()
        assert item.fgColor == QColor("black")
        assert item.bgColor == QColor("transparent")
        assert item.family == ""
        assert item.underline == False
        assert item.pointSize == None
        assert item.strikeout == False
        assert item.weight == None

    def test_factory(self):
        item = f_style()

    def test_set(self, ddb):
        item = ddb.Style()
        item.set(**{"underline": True})
        assert item.underline
        item.set(**{"bgColor": "red"})
        assert item._bgColor == QColor("red").rgba()
        item.set(**{"fgColor": "red"})
        assert item._fgColor == QColor("red").rgba()


class TestEquationModel:
    def test_init(self, ddb):
        a = EquationSection(page=f_page().id)
        assert a.content == ""

    def test_factory(self, ddbr):
        a = f_equationSection(content="1\u2000    \n__ + 1\n15    ")
        assert a.content == "1\u2000    \n__ + 1\n15    ", "1/15 + 1"
        a = f_equationSection(content="     \n1 + 1\n     ")
        assert a.content == "     \n1 + 1\n     "

    def test_set(self, ddb):
        a = f_equationSection()
        assert a.set(content="   ", curseur=1)["content"] == ""
        assert a.set(content="   ", curseur=3)["curseur"] == 0
        assert a.set(content="1+2", curseur=2)["content"] == "1+2"
        assert a.set(content="1+2", curseur=9)["curseur"] == 9


class BaseTestColorMixin:
    def __init__(self, _bgColor=None, _fgColor=None):
        self._fgColor = _fgColor
        self._bgColor = _bgColor


class YupMixin(BaseTestColorMixin, ColorMixin):
    _fgColor = None
    _bgColor = None

    def __init__(self, bgColor=None, fgColor=None, **kwargs):
        kwargs = self.adjust_kwargs_color(bgColor, fgColor, kwargs)
        super().__init__(**kwargs)


class TestColorMixin:
    def test_fgcolor_mixin(self):
        a = YupMixin()

        assert a.fgColor == QColor("transparent")
        assert a._fgColor == None

        a.fgColor = "red"
        assert a.fgColor == QColor("red")
        assert a._fgColor == 4294901760

        a.fgColor = QColor("blue")
        assert a.fgColor == QColor("blue")
        assert a._fgColor == 4278190335

        a.fgColor = 4294901760
        assert a.fgColor == QColor("red")
        assert a._fgColor == 4294901760

        a.fgColor = (0, 0, 255)
        assert a.fgColor == QColor("blue")
        assert a._fgColor == 4278190335

        a.fgColor = [1, 1, 1]  # not supported no changed
        assert a.fgColor == QColor("blue")
        assert a._fgColor == 4278190335

    def test_bgcolor_mixin(self):
        a = YupMixin()

        assert a.bgColor == QColor("transparent")
        assert a._bgColor == None

        a.bgColor = "red"
        assert a.bgColor == QColor("red")
        assert a._bgColor == 4294901760

        a.bgColor = QColor("blue")
        assert a.bgColor == QColor("blue")
        assert a._bgColor == 4278190335

        a.bgColor = 4294901760
        assert a.bgColor == QColor("red")
        assert a._bgColor == 4294901760

        a.bgColor = (0, 0, 255)
        assert a.bgColor == QColor("blue")
        assert a._bgColor == 4278190335

        a.bgColor = [1, 1, 1]  # not supported no changed
        assert a.bgColor == QColor("blue")
        assert a._bgColor == 4278190335

    def test_adjust_kwargs(self):
        a = YupMixin(fgColor="red", bgColor="blue")
        assert a.fgColor == QColor("red")
        assert a.bgColor == QColor("blue")


@pytest.fixture
def position_mixed(reset_db):
    def setup():
        db = Database()

        class Referent(db.Entity):
            mixeds = Set("Mixed")

        class Mixed(db.Entity, PositionMixin):
            ref = Required(Referent)
            referent_attribute_name = "ref"
            _position = Required(int)
            aaas = Set("MixedChild")

            def __init__(self, position=None, ref=None, **kwargs):
                with self.init_position(position, ref) as _position:
                    super().__init__(ref=ref, _position=_position, **kwargs)

            def before_delete(self):
                self.before_delete_position()

            def after_delete(self):
                self.after_delete_position()

        class SubMixed(Mixed):
            base_class_position = Mixed

        class MixedChild(db.Entity, PositionMixin):
            referent_attribute_name = "aaa"
            aaa = Required(Mixed)
            _position = Required(int)

            def __init__(self, position=None, aaa=None, **kwargs):
                with self.init_position(position, aaa) as _position:
                    super().__init__(aaa=aaa, _position=_position, **kwargs)

            def before_delete(self):
                self.before_delete_position()

            def after_delete(self):
                self.after_delete_position()

        db.bind(provider="sqlite", filename=":memory:")
        db.generate_mapping(create_tables=True)
        with db_session:
            rf = Referent()
            flush()
            x = Mixed(ref=rf)
            flush()
            y = Mixed(ref=rf)
            flush()
            z = Mixed(ref=rf)
            return Referent, Mixed, SubMixed, MixedChild, rf, x, y, z

    return setup


class TestPositionMixin:
    def test_create_ete_entity(self, position_mixed):
        Referent, Mixed, SubMixed, MixedChild, ref, x, y, z = position_mixed()
        with db_session:
            x = Mixed[1]
            y = Mixed[2]
            z = Mixed[3]
            assert x.position == 0
            assert y.position == 1
            assert z.position == 2

    @pytest.mark.parametrize("todel, un, deux", [(1, 2, 3), (2, 1, 3), (3, 1, 2),])
    def test_delete_recalculate(self, todel, un, deux, position_mixed):
        Referent, Mixed, SubMixed, MixedChild, ref, x, y, z = position_mixed()

        with db_session:
            Mixed[todel].delete()

        with db_session:
            assert Mixed[un].position == 0
            assert Mixed[deux].position == 1

    @pytest.mark.parametrize(
        "tomove, where, un, deux, trois",
        [
            (2, 0, 1, 0, 2),
            (2, 1, 0, 1, 2),
            (2, 2, 0, 2, 1),
            (1, 0, 0, 1, 2),
            (1, 1, 1, 0, 2),
            (1, 2, 2, 0, 1),
            (3, 0, 1, 2, 0),
            (3, 1, 0, 2, 1),
            (3, 2, 0, 1, 2),
        ],
    )
    def test_set_position(self, tomove, where, un, deux, trois, position_mixed):
        Referent, Mixed, SubMixed, MixedChild, ref, x, y, z = position_mixed()
        with db_session:
            Mixed[tomove].position = where
            assert Mixed[1].position == un
            assert Mixed[2].position == deux
            assert Mixed[3].position == trois

    @pytest.mark.parametrize(
        "where, un, deux, trois, quatre",
        [(1, 0, 2, 3, 1), (0, 1, 2, 3, 0), (2, 0, 1, 3, 2), (20, 0, 1, 2, 3),],
    )
    def test_insert_at(self, position_mixed, where, un, deux, trois, quatre):
        Referent, Mixed, SubMixed, MixedChild, ref, x, y, z = position_mixed()
        with db_session:
            a = Mixed(ref=ref.id, position=where)
        with db_session:
            assert Mixed[1].position == un
            assert Mixed[2].position == deux
            assert Mixed[3].position == trois
            assert Mixed[4].position == quatre

    def test_multiple_add_on_dame_db_session(self, position_mixed):
        Referent, Mixed, SubMixed, MixedChild, ref, x, y, z = position_mixed()
        with db_session:
            s = Mixed(ref=ref.id)
            t = Mixed(ref=ref.id)
        with db_session:
            assert s.position == 3
            assert t.position == 4

    def test_inheritance(self, position_mixed):
        Referent, Mixed, SubMixed, MixedChild, ref, x, y, z = position_mixed()
        with db_session:
            s = SubMixed(ref=ref.id)
            t = SubMixed(ref=ref.id)
        with db_session:
            assert s.position == 3
            assert t.position == 4

    def test_remove_with_relation(self, position_mixed):
        Referent, Mixed, SubMixed, MixedChild, ref, x, y, z = position_mixed()

        with db_session:
            MixedChild(aaa=x.id)
            MixedChild(aaa=x.id)
            MixedChild(aaa=x.id)
        with db_session:
            Mixed[x.id].delete()


class TestUtilisateur:
    def test_factory(self):
        assert f_user()

    def test_last_used(self, ddb):
        u = f_user()
        assert u.last_used == 0
        u.last_used = 2014
        assert u.to_dict()["last_used"] == 2014

    def test_user(self, ddb):
        u = f_user()
        w = Utilisateur.user()
        assert u == w
