import itertools
import uuid
from typing import List
from datetime import datetime, timedelta, date

from PySide2.QtGui import QFont, QColor
from fixtures import compare_items, check_is_range, wait

import pytest
from package.database.mixins import PositionMixin, ColorMixin
from package.exceptions import MyCartableOperationError
from pony.orm import flush, Database, make_proxy, Set, Required, db_session


def test_creation_all(fk):
    an = fk.f_annee()
    goupe = fk.f_groupeMatiere(nom="aa", annee=an.id)
    a = fk.f_matiere(groupe=goupe)
    fk.f_section()


class TestAnnee:
    def test_get_matieres(self, fk):
        with db_session:
            an = fk.f_annee(id=2017)
            assert an.get_matieres()[:] == []
        with db_session:
            g1 = fk.f_groupeMatiere(annee=2017)
            g2 = fk.f_groupeMatiere(annee=2017)
            g3 = fk.f_groupeMatiere(annee=2015)
            g4 = fk.f_groupeMatiere(annee=2017)
            g5 = fk.f_groupeMatiere(annee=2016)
            a = fk.f_matiere(nom="a", groupe=g1)
            b = fk.f_matiere(nom="b", groupe=g2)
            c = fk.f_matiere(nom="c", groupe=g3)
            d = fk.f_matiere(nom="d", groupe=g4)
            f = fk.f_matiere(nom="e", groupe=g5)
            assert an.get_matieres()[:] == [a, b, d]

    def test_to_dict(self, fk):
        with db_session:
            user = fk.db.Utilisateur.user()
        a = fk.f_annee(id=234, niveau="omjlihlm", user=user)
        with db_session:
            assert a.to_dict() == {
                "id": 234,
                "niveau": "omjlihlm",
                "user": str(user.id),
            }


class TestPage:
    def test_modified(self, ddb, fk):
        avant = datetime.utcnow()
        wait()
        s = fk.f_page(created=datetime.utcnow())
        s.to_dict()  # flush

        wait()
        apres = datetime.utcnow()
        assert s.created == s.modified
        assert avant < s.created < apres

    def test_update_modified_when_updated(self, ddb, fk):
        a = fk.f_page()
        avant = a.modified
        a.titre = "omkmo"
        flush()
        assert a.modified != avant

    def test_recents(self, ddb, fk):
        g2019 = fk.f_groupeMatiere(annee=2019)
        g2018 = fk.f_groupeMatiere(annee=2018)
        m2019 = fk.f_matiere(groupe=g2019)
        m2018 = fk.f_matiere(groupe=g2018)
        ac2019 = fk.f_activite(matiere=m2019.id)
        ac2018 = fk.f_activite(matiere=m2018.id)
        for i in range(50):
            fk.f_page(activite=ac2018.id)
            fk.f_page(activite=ac2019.id)

        # test query
        assert ddb.Page.select().count() == 100
        recents = ddb.Page._query_recents(ddb.Page, 2019)[:]
        assert len(recents) == 50
        assert all(x.activite.matiere.groupe.annee.id == 2019 for x in recents)
        old = recents[0]
        for i in recents[1:]:
            assert old.modified > i.modified
            old = i

        # formatted result
        a = fk.f_page(created=datetime.utcnow(), activite=ac2019.id)
        res = a.to_dict()
        res["matiere"] = str(a.activite.matiere.id)
        first_dict = ddb.Page.recents(2019)[0]
        assert first_dict == res

    def test_to_dict(self, ddb, fk):
        d = datetime.utcnow()
        p = fk.f_page(created=d, titre="bl")
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

    def test_nouvelle_page(
        self,
        ddb,
        fk,
    ):
        a = fk.f_matiere().to_dict()
        ac = fk.f_activite(matiere=a["id"])
        flush()
        b = ddb.Page.new_page(activite=ac.id, titre="bla")
        assert ddb.Page.get(id=b["id"], titre="bla", activite=ac.id)

    def test_content(self, fk):
        a = fk.f_page()
        sections = fk.b_section(10, page=a.id)
        others = fk.b_section(10)
        with db_session:
            compare_items(a.content, sections)
        prev = None
        with db_session:
            for i in a.content:
                if prev:
                    assert i.position > prev.position
                prev = i


class TestGroupeMatiere:
    def test_delete_mixin_position(self, fk):
        GroupeMatiere = fk.db.GroupeMatiere
        a = fk.f_groupeMatiere(annee=2019)
        b = fk.f_groupeMatiere(annee=2019)
        with db_session:
            assert GroupeMatiere[a.id].position == 0
            assert GroupeMatiere[b.id].position == 1
            GroupeMatiere[a.id].delete()
        with db_session:
            assert GroupeMatiere[b.id].position == 0

    def test_color_mixin(self, fk):
        GroupeMatiere = fk.db.GroupeMatiere
        fk.f_annee(id=1234)
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
    def test_to_dict(self, ddb, fk):
        fk.f_matiere()
        groupe = fk.f_groupeMatiere(annee=2019)
        a = fk.f_matiere(
            nom="Géo", groupe=groupe, _fgColor=4294967295, _bgColor=4294901760
        )
        pages = [fk.b_page(3, matiere=2) for x in a.activites]
        x = fk.f_activite(matiere=a.id)
        y = fk.f_activite(matiere=a.id)
        z = fk.f_activite(matiere=a.id)
        assert a.to_dict() == {
            "position": 0,
            "id": str(a.id),
            "nom": "Géo",
            "activites": [str(x.id), str(y.id), str(z.id)],
            "groupe": str(groupe.id),
            "fgColor": QColor("white"),
            "bgColor": QColor("red"),
        }

    def test_init(self, ddb, fk):
        gp = fk.f_groupeMatiere()
        an = fk.f_annee()
        a = ddb.Matiere(
            nom="bla",
            groupe=gp.id,
            _fgColor=4294967295,
            _bgColor=4294901760,
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

    def test_delete_mixin_position(self, fk):
        Matiere = fk.db.Matiere
        a = fk.f_matiere()
        b = fk.f_matiere(groupe=a.groupe.id)
        with db_session:
            assert Matiere[a.id].position == 0
            assert Matiere[b.id].position == 1
            Matiere[a.id].delete()
        with db_session:
            assert Matiere[b.id].position == 0

            # a.before_delete_position = Ma

    def test_color_mixin(self, fk):
        Matiere = fk.db.Matiere
        a = fk.f_groupeMatiere()
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

    def test_page_par_section(self, fk):
        Matiere = fk.db.Matiere
        m = fk.f_matiere(nom="Math", _bgColor=4294967295, _fgColor=4294901760)
        un = fk.f_activite(nom="un", matiere=m.id)
        deux = fk.f_activite(nom="deux", matiere=m.id)
        trois = fk.f_activite()
        w = fk.b_page(
            3, activite=deux, titre="pagedeux", created=datetime(1212, 12, 12)
        )
        x = fk.b_page(3, activite=un, titre="pageun", created=datetime(1111, 11, 11))

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
            ]


class TestActivite:
    def test_delete_mixin_position(self, fk):
        a = fk.b_activite(2)
        with db_session:
            assert fk.db.Activite[a[0].id].position == 0
            assert fk.db.Activite[a[1].id].position == 1
            fk.db.Activite[a[0].id].delete()
        with db_session:
            assert fk.db.Activite[a[1].id].position == 0


class TestSection:
    def test_init(self, fk):
        p = fk.f_page()
        fk.f_section(page=p.id)
        with db_session:
            s = fk.db.Section(page=p.id)
        with db_session:
            x = fk.db.Section(page=p.id)
        assert s._position == 1
        assert x._position == 2
        with db_session:
            z = fk.db.Section(page=p.id, position=1)
            assert fk.db.Section[s.id].position == 2
            assert fk.db.Section[x.id].position == 3

    def test_get_with_string(self, fk):
        x = fk.f_section()
        strid = str(x.id)
        with db_session:
            z = fk.db.Section[strid]

    def test_delete_mixin_position(self, fk):
        Section = fk.db.Section
        a = fk.f_page()
        x = fk.f_section(page=a.id)
        y = fk.f_section(page=a.id)
        with db_session:
            assert Section[x.id].position == 0
            assert Section[y.id].position == 1
            Section[x.id].delete()
        with db_session:
            assert Section[y.id].position == 0

    def test_position_property(self, ddb, fk):
        p = fk.f_page()
        with db_session:
            z = fk.f_section(page=p.id)
            flush()
            x = fk.f_section(page=p.id)
            flush()
            assert z.position == 0
            assert x.position == 1
            x.position = 0
            assert z.position == 1
            assert x.position == 0

    def test_inheritance_position(self, fk):
        page = fk.f_page()
        fk.f_section(page=page.id)
        with db_session:
            s = fk.db.TextSection(page=page.id)
            t = fk.db.EquationSection(page=page.id)
            u = fk.db.Section(page=page.id)
            assert s.position == 1
            assert t.position == 2
            assert u.position == 3

    def test_inheritance_position2(self, fk):
        page = fk.f_page()
        r = fk.f_section(page=page.id)
        with db_session:
            s = fk.db.TextSection(page=page.id)
        with db_session:
            t = fk.db.EquationSection(page=page.id)
        with db_session:
            u = fk.db.Section(page=page.id)
        with db_session:
            assert fk.db.Section[r.id].position == 0
            assert fk.db.Section[s.id].position == 1
            assert fk.db.Section[t.id].position == 2
            assert fk.db.Section[u.id].position == 3

    def test_to_dict(self, fk):
        a = datetime.utcnow()
        x = fk.f_section(created=a, td=True)
        assert x["created"] == a.isoformat()
        assert x["modified"] == a.isoformat()

    def test_before_insert_no_position(self, ddb, fk):
        """"remember factory are flushed"""
        a = fk.f_page()
        b = fk.f_section(page=a.id)
        flush()
        assert b.position == 0
        c = fk.f_section(page=a.id)
        flush()
        assert b.position == 0
        assert c.position == 1

    def test_before_insert_position_to_high(self, ddb, fk):
        a = fk.f_page()
        b = fk.f_section(page=a.id)
        flush()
        assert b.position == 0
        c = fk.f_section(page=a.id, position=3)
        flush()
        assert b.position == 0
        assert c.position == 1

    def test_update_position(self, ddb, fk):
        a = fk.f_page()
        b = fk.b_section(5, page=a.id)
        modified_item = b[0].modified
        flush()
        c = fk.f_section(page=a.id, position=3)
        flush()
        # test new item
        assert c.position == 3

        # position n'influence pas la date de modif de section
        assert a.content[0].modified == modified_item

        # inflence l date de modif de page
        page_modified = a.modified
        wait()
        fk.f_section(page=a.id, created=datetime.utcnow())
        assert page_modified < a.modified

    def test_before_update(self, fk):
        with db_session:
            a = make_proxy(fk.f_section())
            b = a.modified
        with db_session:
            a.created = datetime.utcnow()
        with db_session:
            assert a.modified > b
            assert a.page.modified == a.modified

    def test_before_insert(self, fk):
        avant = datetime.utcnow()
        wait()
        s = fk.f_section(created=datetime.utcnow())
        wait()
        apres = datetime.utcnow()
        assert avant < s.created < apres
        assert s.created == s.modified
        with db_session:
            assert fk.db.Page[s.page.id].modified >= s.modified

    def test_update_position__and_time_on_delete(self, fk):
        p = fk.f_page()
        s0 = fk.f_section(page=p.id)
        s1 = fk.f_section(page=p.id)
        s2 = fk.f_section(page=p.id)

        with db_session:
            now = fk.db.Page[p.id].modified
            wait()
            fk.db.Section[s0.id].delete()

        with db_session:
            # resultat avec décalage
            assert fk.db.Section[s1.id].position == 0
            assert fk.db.Section[s2.id].position == 1
            # page mis à jour
            assert now < fk.db.Page[p.id].modified

    @pytest.mark.parametrize(
        "start, new_pos, poses",
        [
            (2, 3, (0, 1, 3, 2, 4)),
            (3, 1, (0, 2, 3, 1, 4)),
        ],
    )
    def test_update_position_change_position_descend(self, fk, start, new_pos, poses):
        a = fk.f_page()
        secs = []
        with db_session:
            for i in range(5):
                z = fk.db.Section(page=a.id, position=i)
                flush()
                secs.append(z)
            for i, e in enumerate(secs):
                assert e.position == i
        with db_session:
            x = fk.db.Section[secs[start].id]
            x.position = new_pos
        with db_session:
            for index, value in enumerate(poses):
                assert fk.db.Section[secs[index].id].position == value


class TestImageSection:
    def test_factory(self, fk):
        a = fk.f_imageSection(path="mon/path")
        assert a.path == "mon/path"

    def test_to_dict(self, fk):
        a = fk.f_imageSection(path="mon/path", td=True)
        assert a["path"] == "mon/path"
        assert a["annotations"] == []


class TestTextSection:
    def test_factory(self, fk):
        assert fk.f_textSection(text="bla").text == "bla"

    def test_default_is_empty_string(self, ddb, fk):
        p = fk.f_page()
        tex = ddb.TextSection(page=p.id)
        assert tex.text == "<body></body>"


class TestTableDataSection:
    def test_datas(self, ddb, fk):
        p = fk.f_page()
        a = ddb.TableDataSection(
            _datas='["", "", "", "", "", ""]', rows=3, columns=2, page=p.id
        )
        assert a.datas == ["", "", "", "", "", ""]

    def test_update_datas(self, ddb, fk):
        p = fk.f_page()
        a = ddb.TableDataSection(
            _datas='["", "", "", "", "", ""]', rows=3, columns=2, page=p.id
        )
        a.update_datas(4, "g")
        assert a.datas == ["", "", "", "", "g", ""]

    def test_to_dict(self, ddb, fk):
        p = fk.f_page()
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
    def test_init(self, ddb, fk):
        x = fk.f_page()
        # normal
        a = ddb.OperationSection(string="1+2", page=x.id)
        assert a._datas == '["", "", "", "1", "+", "2", "", ""]'
        assert a.datas == ["", "", "", "1", "+", "2", "", ""]
        assert a.rows == 4
        assert a.columns == 2

    def test_error_in_init(self, ddb, fk):
        with pytest.raises(MyCartableOperationError) as err:
            ddb.OperationSection(string="1(2")
        assert str(err.value) == "1(2 est une entrée invalide"

    def test_datas(self, ddb, fk):
        fk.f_page()

        # do not use content if None
        with pytest.raises(TypeError):
            a = ddb.OperationSection(page=1)

    def test_to_dict(self, fk):
        item = fk.f_additionSection(string="259+135")
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

    def test_update_datas(self, fk):
        item = fk.f_additionSection(string="259+135")
        with db_session:
            fk.db.Section[item.id].update_datas(15, 4)

        with db_session:
            assert fk.db.Section[item.id].datas[15] == 4


class TestAddditionSection:
    def test_factory(self, fk):
        assert fk.f_additionSection(string="15+3").datas == [
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

        fk.f_additionSection()

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
    def test_get_editables(self, ddb, string, res, fk):
        x = fk.f_additionSection(string=string)
        assert x.get_editables() == res


class TestSoustractionSection:
    def test_factory(self, fk):
        res = (
            [
                "",
                "",
                "1",
                "",
                "",
                "5",
                "",
                "-",
                "",
            ]
            + [
                "",
                "",
                "",
                "3",
                "",
                "",
                "",
                "",
            ]
            + [
                "",
                "",
                "",
                "",
            ]
        )
        assert fk.f_soustractionSection(string="15-3").datas == res

        fk.f_soustractionSection()

    def test_lines(self, ddb, fk):
        a = fk.f_soustractionSection(string="24-13")
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
    def test_get_editables(self, ddb, string, res, fk):
        x = fk.f_soustractionSection(string=string)
        assert x.get_editables() == res


class TestMultiplicationSection:
    def test_factory(self, fk):
        assert fk.f_multiplicationSection(string="1*2").datas == [
            "",
            "",
            "",
            "2",
            "x",
            "1",
            "",
            "",
        ]

        fk.f_multiplicationSection()

    def test_properties(self, ddb, fk):
        a = fk.f_multiplicationSection(string="12*34")
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
            (
                "2,2*5,5",
                {3, 9} | set(range(25, 48)) - set(range(24, 48, 6)),
            ),
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
    def test_get_editables(self, ddb, string, res, fk):
        x = fk.f_multiplicationSection(string=string)
        assert x.get_editables() == res


class TestDivisionSection:
    def test_factory(self, ddb, fk):
        x = fk.f_divisionSection(string="34/3")
        assert x.dividende == "34"
        assert x.diviseur == "3"

    def test_is_ligne_dividende(self, fk):
        tm = fk.f_divisionSection("264/11")
        check_is_range(tm, "is_ligne_dividende", range(9))

    def test_is_ligne_last(self, fk):
        tm = fk.f_divisionSection("264/11")
        check_is_range(tm, "is_ligne_last", range(36, 45))

    @pytest.mark.parametrize(
        "string, res",
        [
            # ("5/4", set(range(84)) - {1}),
            (
                "264/11",
                {10, 13, 16, 19, 22, 25} | {28, 31, 34, 37, 40, 43},
            ),
        ],
    )
    def test_get_editables(self, string, res, fk):
        x = fk.f_divisionSection(string=string)
        assert x.get_editables() == res

    #     # 'rows': 5, 'columns': 9, '
    #
    #     # '', 'X', '',  '*', 'Y', '', '*', 'Z', '' //8
    #     # '', '*', '*', '',  '*', '*', '', '*', '', // 17
    #     # '', '*', '', '*',  '*', '', '*', '*', '', // 26
    #     # '', '*', '*', '',  '*', '*', '', '*', '', // 35
    #     # '', '*', '', '',   '*', '',  '', '*', '' , //44

    def test_to_dict(self, fk):
        x = fk.f_divisionSection(string="5/4")
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

    def test_as_num(self, fk):
        x = fk.f_divisionSection(string="5/4")
        assert x.diviseur_as_num == 4
        assert x.dividende_as_num == 5

        x = fk.f_divisionSection(string="5,333333/4,1")
        assert x.diviseur_as_num == 4.1
        assert x.dividende_as_num == 5.333333


class TestAnnotations:
    def test_init(self, ddb, fk):
        s = fk.f_section()
        x = ddb.Annotation(x=0.1, y=0.4, section=s.id)
        x.style.flush()
        assert isinstance(x.style.styleId, uuid.UUID)

    def test_factory(self, fk):
        a = fk.f_annotation()
        assert isinstance(a.id, uuid.UUID)

    def test_init_and_to_dict(self, ddb, fk):
        s = fk.f_section()
        x = ddb.Annotation(x=0.1, y=0.4, section=s.id, style={"bgColor": "red"})
        assert x.style.bgColor == QColor("red")

        r = x.to_dict()
        assert r["x"] == 0.1
        assert r["y"] == 0.4
        assert r["section"] == ddb.Section[s.id]
        assert r["bgColor"] == QColor("red")
        assert r["fgColor"] == QColor("black")
        assert r["id"] == str(x.id)

    def test_set(self, fk):
        x = fk.f_annotation(x=0.3)
        with db_session:
            x = fk.db.Annotation[x.id]
            assert not x.style.underline
            x.set(**{"x": 0.7, "style": {"underline": True}, "attrs": {"y": "0.234"}})
            assert x.x == 0.7
            assert x.style.underline
            assert x.y == 0.234
            x.set(**{"x": 0.9})
            assert x.x == 0.9

    def test_add_modify_section_and_page_modified_attribute(self, fk):
        p = fk.f_page()
        before_p = p.modified
        s = fk.f_section(page=p.id, created=datetime.utcnow())
        before = s.modified

        wait()
        a = fk.f_annotation(section=s.id)

        with db_session:
            n = fk.db.Section[s.id]
            after = n.modified
            wait()
            after_p = n.page.modified

        assert before < after
        assert before_p < after_p

    #
    def test_delete_modify_section_and_page_modified_attribute(self, fk):
        p = fk.f_page()
        s = fk.f_section(page=p.id, created=datetime.utcnow())
        a = fk.f_annotation(section=s.id)
        wait()
        with db_session:
            n = fk.db.Section[s.id]
            before = n.modified
            before_p = n.page.modified
        wait()
        with db_session:
            fk.db.Annotation[a.id].delete()

        with db_session:
            n = fk.db.Section[s.id]
            after = n.modified
            after_p = n.page.modified

        assert before < after
        assert before_p < after_p

    def test_delete_not_fail_if_section_deleted(self, fk):
        a = fk.f_annotation()
        with db_session:
            s = fk.db.Section[a.section.id]
            a = fk.db.Annotation[a.id]
            s.delete()
            a.delete()

    def test_annotation_text(self, fk):
        an = fk.f_annotationText(text=" jihkujgy ")
        assert an.text == " jihkujgy "

    def test_annotation_dessin(self, fk):
        an = fk.f_annotationText(text=" jihkujgy ")
        assert an.text == " jihkujgy "

    def test_annotation_dession(self, fk):
        an = fk.f_annotationDessin()

    def test_getitem(self, fk):
        fk.f_annotation()
        fk.f_annotationDessin()
        fk.f_annotationText()

        with db_session:
            annots = fk.db.Annotation.select()[:]
            a = annots[0].as_type()
            assert isinstance(a, fk.db.Annotation)
            a = annots[1].as_type()
            assert isinstance(a, fk.db.AnnotationDessin)
            a = annots[2].as_type()
            assert isinstance(a, fk.db.AnnotationText)


class TestTableauSection:
    def test_init(self, ddb, fk):
        x = fk.f_page()
        # normal
        a = ddb.TableauSection(lignes=3, colonnes=4, page=x.id)
        a.flush()
        assert a.cells.count() == 12
        # si pas d'erreur c que pq ok
        assert [ddb.TableauCell[a.id, y, x] for y in range(3) for x in range(4)]

        b = fk.f_tableauSection()

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
    def test_init_with_model(self, fk, modele, zero_0, zero_1, un_0, un_1):
        x = fk.f_tableauSection(2, 2, modele)
        with db_session:
            a = fk.db.TableauSection[x.id]
            assert fk.db.TableauCell[a, 0, 0].style.bgColor.rgba() == zero_0.rgba()
            assert fk.db.TableauCell[a, 0, 1].style.bgColor.rgba() == zero_1.rgba()
            assert fk.db.TableauCell[a, 1, 0].style.bgColor.rgba() == un_0.rgba()
            assert fk.db.TableauCell[a, 1, 1].style.bgColor.rgba() == un_1.rgba()

    def test_to_dict(self, ddb, fk):
        item = fk.f_tableauSection(lignes=3, colonnes=4)

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

    def test_get_par_ligne(self, ddb, fk):
        TableauCell = ddb.TableauCell
        TableauSection = ddb.TableauSection
        t = fk.f_tableauSection(lignes=5, colonnes=4)
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
    @pytest.fixture()
    def peupler_tableau_manipulation(fk):
        def wraped():
            with db_session:
                a = fk.f_tableauSection(3, 4)  # premiere colone : 0,4,8
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

        return wraped

    def test_insert_one_line(self, peupler_tableau_manipulation):
        a, cells = peupler_tableau_manipulation()
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

    def test_insert_one_line_start(self, peupler_tableau_manipulation):
        a, cells = peupler_tableau_manipulation()
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

    def test_insert_one_avant_line_dernier(self, peupler_tableau_manipulation):
        a, cells = peupler_tableau_manipulation()
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

    def test_insert_one_apres_dernier(self, peupler_tableau_manipulation):
        a, cells = peupler_tableau_manipulation()
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

    def test_insert_append_one_line(self, peupler_tableau_manipulation):
        a, cells = peupler_tableau_manipulation()
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

    def test_remove_line_middle(self, peupler_tableau_manipulation):
        a, cells = peupler_tableau_manipulation()
        with db_session:
            a.remove_on_line(1)
        with db_session:
            assert a.cells.count() == 8
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[4] == cells[8]

    def test_remove_line_last(self, peupler_tableau_manipulation):
        a, cells = peupler_tableau_manipulation()
        with db_session:
            a.remove_one_line(2)
        with db_session:
            assert a.cells.count() == 8
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[4] == cells[4]

    def test_remove_line_middle(self, peupler_tableau_manipulation):
        a, cells = peupler_tableau_manipulation()
        with db_session:
            a.remove_one_line(0)
        with db_session:
            assert a.cells.count() == 8
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[4]
            assert cells_after[4] == cells[8]

    @staticmethod
    @pytest.fixture()
    def peupler_tableau_manip_colonnes(fk):
        def wrap():
            with db_session:
                a = fk.f_tableauSection(3, 4)
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

        return wrap

    def test_insert_one_col_middle(self, peupler_tableau_manip_colonnes):
        a, cells = peupler_tableau_manip_colonnes()
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

    def test_insert_one_col_start(self, peupler_tableau_manip_colonnes):
        a, cells = peupler_tableau_manip_colonnes()
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

    def test_insert_one_col_avant_dernier(self, peupler_tableau_manip_colonnes):
        a, cells = peupler_tableau_manip_colonnes()
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

    def test_insert_one_col__dernier(self, peupler_tableau_manip_colonnes):
        a, cells = peupler_tableau_manip_colonnes()
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

    def test_insert_append_colonne(self, peupler_tableau_manip_colonnes):
        a, cells = peupler_tableau_manip_colonnes()
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

    def test_remove_one_col_middle(self, peupler_tableau_manip_colonnes):
        a, cells = peupler_tableau_manip_colonnes()
        with db_session:
            a.remove_one_column(2)
        with db_session:
            assert a.cells.count() == 9
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[0]
            assert cells_after[1] == cells[1]
            assert cells_after[2] == cells[3]

    def test_remove_one_col_start(self, peupler_tableau_manip_colonnes):
        a, cells = peupler_tableau_manip_colonnes()
        with db_session:
            a.remove_one_column(0)
        with db_session:
            assert a.cells.count() == 9
            cells_after = [x.to_dict(exclude=["x", "y"]) for x in a.get_cells()[:]]
            [x["style"].pop("styleId") for x in cells_after]
            assert cells_after[0] == cells[1]
            assert cells_after[1] == cells[2]
            assert cells_after[2] == cells[3]

    def test_remove_one_col_end(self, peupler_tableau_manip_colonnes):
        a, cells = peupler_tableau_manip_colonnes()
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
    def test_init(self, ddb, fk):
        # simple
        t = fk.f_tableauSection(lignes=0)
        a = ddb.TableauCell(tableau=t, x=0, y=0)
        assert a.x == 0
        assert a.y == 0
        assert a.style.bgColor == QColor("transparent")
        assert ddb.TableauCell[a.tableau, 0, 0] == a
        b = ddb.TableauCell(tableau=t, x=0, y=1, style={"bgColor": "red"})
        assert b.style._bgColor == 4294901760

    def test_factory(self, fk):
        t = fk.f_tableauSection(lignes=0, colonnes=0)
        fk.f_tableauCell(tableau=t.id)
        fk.f_tableauCell(x=1, tableau=t.id)

    def test_to_dict(self, fk):
        s = fk.f_style(bgColor="red")
        b = fk.f_tableauCell(x=2, y=0, style=s.styleId, texte="bla")
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

    def test_set(self, fk):
        x = fk.f_tableauCell(texte="bla")
        with db_session:
            x = fk.db.TableauCell[x.tableau.id, 0, 0]
            assert not x.style.underline
            x.set(**{"texte": "bbb"})
            assert x.texte == "bbb"
            x.set(**{"texte": "aaa", "style": {"underline": True}})
            assert x.texte == "aaa"
            assert x.style.underline


class TestStyle:
    def test_init(self, ddb, fk):
        # set tout
        item = ddb.Style(
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
        item = ddb.Style()
        assert item.fgColor == QColor("black")
        assert item.bgColor == QColor("transparent")
        assert item.family == ""
        assert item.underline == False
        assert item.pointSize == None
        assert item.strikeout == False
        assert item.weight == None

    def test_factory(self, fk):
        item = fk.f_style()

    def test_set(self, ddb, fk):
        item = ddb.Style()
        item.set(**{"underline": True})
        assert item.underline
        item.set(**{"bgColor": "red"})
        assert item._bgColor == QColor("red").rgba()
        item.set(**{"fgColor": "red"})
        assert item._fgColor == QColor("red").rgba()


class TestEquationModel:
    def test_init(self, ddb, fk):
        a = ddb.EquationSection(page=fk.f_page().id)
        assert a.content == ""

    def test_factory(self, fk):
        a = fk.f_equationSection(content="1\u2000    \n__ + 1\n15    ")
        assert a.content == "1\u2000    \n__ + 1\n15    ", "1/15 + 1"
        a = fk.f_equationSection(content="     \n1 + 1\n     ")
        assert a.content == "     \n1 + 1\n     "

    def test_set(self, ddb, fk):
        a = fk.f_equationSection()
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
def position_mixed(fk):
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

    @pytest.mark.parametrize(
        "todel, un, deux",
        [
            (1, 2, 3),
            (2, 1, 3),
            (3, 1, 2),
        ],
    )
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
        [
            (1, 0, 2, 3, 1),
            (0, 1, 2, 3, 0),
            (2, 0, 1, 3, 2),
            (20, 0, 1, 2, 3),
        ],
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
    def test_factory(self, fk):
        assert fk.f_user()

    def test_last_used(self, ddb, fk):
        u = fk.f_user()
        assert u.last_used == 0
        u.last_used = 2014
        assert u.to_dict()["last_used"] == 2014

    def test_user(self, ddb, fk):
        u = fk.f_user()
        w = ddb.Utilisateur.user()
        assert u == w


class TestConfiguration:
    def test_get_field(self, ddb):
        c = ddb.Configuration
        assert c._get_field("a") == "str_value"
        assert c._get_field(12) == "int_value"
        assert c._get_field(12.12) == "float_value"
        assert c._get_field(datetime.now()) == "datetime_value"
        assert c._get_field(date.today()) == "date_value"
        assert c._get_field(uuid.uuid4()) == "uuid_value"
        assert c._get_field([1, 2, 3]) == "json_value"
        assert c._get_field({"234": 234}) == "json_value"

    def test_add_option(self, ddb):
        c = ddb.Configuration
        # add part
        c.add("string", "value")
        assert c.option("string") == "value"
        c.add("int", 1)
        assert c.option("int") == 1
        c.add("float", 1.1)
        assert c.option("float") == 1.1
        d = datetime.now()
        c.add("datetime", d)
        assert c.option("datetime") == d
        dt = date.today()
        c.add("date", dt)
        assert c.option("date") == dt
        c.add("list", [1, 2, 3])
        assert c.option("list") == [1, 2, 3]
        c.add("dict", {"kj": "okmlj"})
        assert c.option("dict") == {"kj": "okmlj"}
        u = uuid.uuid4()
        c.add("uuid", u)
        assert c.option("uuid") == u


class TestFrise:
    def test_factory(self, fk):
        f = fk.f_friseSection()
        assert f.height == 400
        g = fk.f_zoneFrise(frise=f.id)
        assert g.ratio == 0.2
        assert g.position == 0
        h = fk.f_zoneFrise(frise=f.id)
        assert h.position == 1

    def test_delete_mixin_position(self, fk):
        frise = fk.f_friseSection()
        ZoneFrise = fk.db.ZoneFrise
        g = fk.f_zoneFrise(frise=frise.id)
        h = fk.f_zoneFrise(frise=frise.id)

        with db_session:
            assert ZoneFrise[g.id].position == 0
            assert ZoneFrise[h.id].position == 1
            ZoneFrise[g.id].delete()
        with db_session:
            assert ZoneFrise[h.id].position == 0

    def test_zonefrise_init_set_to_dict(self, fk):
        ph = fk.f_friseSection()

        with db_session:
            # test _init
            f = fk.db.ZoneFrise(
                frise=ph.id, ratio=0.2, style={"bgColor": "blue"}, texte="bla"
            )
            l = fk.f_friseLegende(texte="aa", relativeX="0.3", side=True, zone=f.id)
            assert f.style.bgColor == "blue"
            # test set
            f.set(ratio=0.5, style={"bgColor": "green"})
            assert f.style.bgColor == "green"
            assert f.ratio == 0.5
            assert f.to_dict() == {
                "frise": str(ph.id),
                "id": str(f.id),
                "position": 0,
                "ratio": 0.5,
                "texte": "bla",
                "separatorText": "",
                "legendes": [
                    {
                        "id": str(l.id),
                        "relativeX": 0.3,
                        "side": True,
                        "texte": "aa",
                        "zone": str(f.id),
                    }
                ],
                "style": {
                    "bgColor": QColor("green"),
                    "family": "",
                    "fgColor": QColor("black"),
                    "pointSize": None,
                    "strikeout": False,
                    "styleId": str(f.style.styleId),
                    "underline": False,
                    "weight": None,
                },
            }

    def test_FriseSection_to_dict(self, fk):
        f = fk.f_friseSection(titre="une frise", height=300)
        g = fk.f_zoneFrise(texte="aaa", frise=f)
        h = fk.f_zoneFrise(texte="bbb", frise=f)
        with db_session:
            item = fk.db.FriseSection[f.id]
            dico = item.to_dict()
            dico.pop("modified")
            assert dico == {
                "classtype": "FriseSection",
                "created": f.created.isoformat(),
                "height": 300,
                "id": str(f.id),
                "page": str(item.page.id),
                "position": 0,
                "titre": "une frise",
                "zones": [
                    {
                        "frise": str(f.id),
                        "id": str(g.id),
                        "position": 0,
                        "ratio": 0.2,
                        "separatorText": "",
                        "legendes": [],
                        "style": {
                            "bgColor": QColor.fromRgbF(0, 0, 0, 0),
                            "family": "",
                            "fgColor": QColor.fromRgbF(0, 0, 0, 1),
                            "pointSize": None,
                            "strikeout": False,
                            "styleId": str(g.style.styleId),
                            "underline": False,
                            "weight": None,
                        },
                        "texte": "aaa",
                    },
                    {
                        "frise": str(f.id),
                        "id": str(h.id),
                        "position": 1,
                        "ratio": 0.2,
                        "separatorText": "",
                        "legendes": [],
                        "style": {
                            "bgColor": QColor.fromRgbF(0, 0, 0, 0),
                            "family": "",
                            "fgColor": QColor.fromRgbF(0, 0, 0, 1),
                            "pointSize": None,
                            "strikeout": False,
                            "styleId": str(h.style.styleId),
                            "underline": False,
                            "weight": None,
                        },
                        "texte": "bbb",
                    },
                ],
            }
