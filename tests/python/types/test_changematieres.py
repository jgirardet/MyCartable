import pytest
from PySide2.QtGui import QColor
from fixtures import check_args
from mycartable.types.changematieres import ChangeMatieres
from pony.orm import db_session


@pytest.fixture()
def cm(ddbr, qapp):
    res = ChangeMatieres()
    res.db = ddbr
    return res


class TestChangeMatieresMixin:
    def test_check_args(self, cm: ChangeMatieres):
        check_args(cm.getActivites, str, list)
        check_args(cm.moveActiviteTo, [str, int], list)
        check_args(cm.removeActivite, str, list)
        check_args(cm.addActivite, [str, bool], list, slot_order=0)
        check_args(cm.addActivite, [str], list, slot_order=1)
        check_args(cm.updateActiviteNom, [str, str])
        check_args(cm.getMatieres, str, list)
        check_args(cm.moveMatiereTo, [str, int], list)
        check_args(cm.removeMatiere, str, list)
        check_args(cm.updateMatiereNom, [str, str])
        check_args(cm.addMatiere, [str, bool], list, slot_order=0)
        check_args(cm.addMatiere, [str], list, slot_order=1)
        check_args(cm.getGroupeMatieres, int, list)
        check_args(cm.moveGroupeMatiereTo, [str, int], list)
        check_args(cm.removeGroupeMatiere, str, list)
        check_args(cm.updateGroupeMatiereNom, [str, str])
        check_args(cm.addGroupeMatiere, str, list)
        check_args(cm.applyGroupeDegrade, [str, QColor], list)
        check_args(cm.reApplyGroupeDegrade, str, list)

    def test_get_activites(self, fk, cm):
        m = fk.f_matiere()
        acs = fk.b_activite(3, nom="machoire", matiere=m)
        fk.b_page(3, activite=acs[0])

        assert cm.getActivites(str(m.id)) == [
            {
                "id": str(acs[0].id),
                "matiere": str(m.id),
                "nom": "machoire",
                "position": 0,
                "nbPages": 3,
            },
            {
                "id": str(acs[1].id),
                "matiere": str(m.id),
                "nom": "machoire",
                "position": 1,
                "nbPages": 0,
            },
            {
                "id": str(acs[2].id),
                "matiere": str(m.id),
                "nom": "machoire",
                "position": 2,
                "nbPages": 0,
            },
        ]

    def test_moveActivite(self, fk, cm):
        m = fk.f_matiere()
        acs = fk.b_activite(3, nom="essetoto", matiere=m)
        assert cm.moveActiviteTo(str(acs[2].id), 0) == [
            {
                "id": str(acs[2].id),
                "matiere": str(m.id),
                "nom": "essetoto",
                "position": 0,
                "nbPages": 0,
            },
            {
                "id": str(acs[0].id),
                "matiere": str(m.id),
                "nom": "essetoto",
                "position": 1,
                "nbPages": 0,
            },
            {
                "id": str(acs[1].id),
                "matiere": str(m.id),
                "nom": "essetoto",
                "position": 2,
                "nbPages": 0,
            },
        ]

    def test_removeActivite(self, fk, cm):
        m = fk.f_matiere()
        acts = fk.b_activite(3, nom="les bizards", matiere=m.id)

        assert cm.removeActivite(str(acts[1].id)) == [
            {
                "id": str(acts[0].id),
                "matiere": str(m.id),
                "nom": "les bizards",
                "position": 0,
                "nbPages": 0,
            },
            {
                "id": str(acts[2].id),
                "matiere": str(m.id),
                "nom": "les bizards",
                "position": 1,
                "nbPages": 0,
            },
        ]

    def test_addActivite(self, cm, fk, ddbr):
        m = fk.f_matiere()
        acts = fk.b_activite(3, nom="bidet", matiere=m)
        res = cm.addActivite(str(acts[0].id))
        with db_session:
            new = ddbr.Activite.select()[:][-1]

        assert res == [
            {
                "id": str(new.id),
                "matiere": str(m.id),
                "nom": "nouvelle",
                "position": 0,
                "nbPages": 0,
            },
            {
                "id": str(acts[0].id),
                "matiere": str(m.id),
                "nom": "bidet",
                "position": 1,
                "nbPages": 0,
            },
            {
                "id": str(acts[1].id),
                "matiere": str(m.id),
                "nom": "bidet",
                "position": 2,
                "nbPages": 0,
            },
            {
                "id": str(acts[2].id),
                "matiere": str(m.id),
                "nom": "bidet",
                "position": 3,
                "nbPages": 0,
            },
        ]

    def test_addActivite_append(self, cm, fk):
        m = fk.f_matiere()
        res = cm.addActivite(str(m.id), True)
        with db_session:
            new = fk.db.Activite.select()[:][-1]
        assert res == [
            {
                "id": str(new.id),
                "matiere": str(m.id),
                "nom": "nouvelle",
                "position": 0,
                "nbPages": 0,
            },
        ]

    def test_updateActiviteNom(self, fk, cm):
        fk.f_activite(nom="bla")
        cm.updateActiviteNom(1, "meuh")
        with db_session:
            assert cm.db.Activite[1].nom == "meuh"

    def test_getMatieres(self, fk, cm):
        groupe = fk.f_groupeMatiere()
        mats = fk.b_matiere(
            3, nom="picotin", bgColor="red", fgColor="blue", groupe=groupe
        )
        ac = fk.f_activite(matiere=mats[0].id)
        pages = fk.b_page(5, activite=ac.id)
        assert cm.getMatieres(str(groupe.id)) == [
            {
                "activites": [str(ac.id)],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": str(groupe.id),
                "id": str(mats[0].id),
                "nom": "picotin",
                "position": 0,
                "nbPages": 5,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": str(groupe.id),
                "id": str(mats[1].id),
                "nom": "picotin",
                "position": 1,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": str(groupe.id),
                "id": str(mats[2].id),
                "nom": "picotin",
                "position": 2,
                "nbPages": 0,
            },
        ]

    def test_moveMatiere(self, fk, cm):
        groupe = fk.f_groupeMatiere()
        mats = fk.b_matiere(
            3, nom="cacahuete coding", bgColor="red", fgColor="blue", groupe=groupe
        )
        assert cm.moveMatiereTo(str(mats[2].id), 1) == [
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": str(groupe.id),
                "id": str(mats[0].id),
                "nom": "cacahuete coding",
                "position": 0,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": str(groupe.id),
                "id": str(mats[2].id),
                "nom": "cacahuete coding",
                "position": 1,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": str(groupe.id),
                "id": str(mats[1].id),
                "nom": "cacahuete coding",
                "position": 2,
                "nbPages": 0,
            },
        ]

    def test_removeMatieres(self, fk, cm):
        groupe = fk.f_groupeMatiere()
        mats = fk.b_matiere(
            3, nom="cerf-vollant", bgColor="red", fgColor="blue", groupe=groupe
        )
        assert cm.removeMatiere(str(mats[1].id)) == [
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": str(groupe.id),
                "id": str(mats[0].id),
                "nom": "cerf-vollant",
                "position": 0,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": str(groupe.id),
                "id": str(mats[2].id),
                "nom": "cerf-vollant",
                "position": 1,
                "nbPages": 0,
            },
        ]

    def test_addMatiere(self, fk, cm):
        groupe = fk.f_groupeMatiere()
        mats = fk.b_matiere(3, nom="rien", bgColor="red", fgColor="blue", groupe=groupe)
        res = cm.addMatiere(str(mats[1].id))
        with db_session:
            new = groupe.matieres.select()[:][-1]
        assert res == [
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": str(groupe.id),
                "id": str(mats[0].id),
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("white"),
                "fgColor": QColor("black"),
                "groupe": str(groupe.id),
                "id": str(new.id),
                "nom": "nouvelle",
                "position": 1,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": str(groupe.id),
                "id": str(mats[1].id),
                "nom": "rien",
                "position": 2,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "groupe": str(groupe.id),
                "id": str(mats[2].id),
                "nom": "rien",
                "position": 3,
                "nbPages": 0,
            },
        ]

    def test_addMatiere_appendd(self, fk, cm):
        groupe = fk.f_groupeMatiere()
        res = cm.addMatiere(str(groupe.id), True)

        with db_session:
            new = groupe.matieres.select()[:][-1]
        assert res == [
            {
                "activites": [],
                "bgColor": QColor.fromRgbF(1.000000, 1.000000, 1.000000, 1.000000),
                "fgColor": QColor.fromRgbF(0.000000, 0.000000, 0.000000, 1.000000),
                "groupe": str(groupe.id),
                "id": str(new.id),
                "nbPages": 0,
                "nom": "nouvelle",
                "position": 0,
            }
        ]

    def test_updateActiviteNom(self, fk, cm):
        m = fk.f_matiere(nom="bla")
        cm.updateMatiereNom(str(m.id), "meuh")
        with db_session:
            assert cm.db.Matiere[str(m.id)].nom == "meuh"

    def test_getGroupeMatieres(self, fk, cm):
        gm = fk.b_groupeMatiere(
            3, annee=2017, nom="rien", bgColor="red", fgColor="blue"
        )
        m = fk.f_matiere(groupe=gm[2])
        ac = fk.f_activite(matiere=m)
        pages = fk.b_page(2, activite=ac)
        assert cm.getGroupeMatieres(2017) == [
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": str(gm[0].id),
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": str(gm[1].id),
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": str(gm[2].id),
                "nom": "rien",
                "position": 2,
                "nbPages": 2,
            },
        ]

    def test_removeGroupeMatiere(self, fk, cm):
        gm = fk.b_groupeMatiere(
            3, annee=2017, nom="rien", bgColor="red", fgColor="blue"
        )
        assert cm.removeGroupeMatiere(str(gm[1].id)) == [
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": str(gm[0].id),
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": str(gm[2].id),
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
        ]

    def test_moveGroupeMatiere(self, fk, cm):
        gm = fk.b_groupeMatiere(
            3, annee=2017, nom="rien", bgColor="red", fgColor="blue"
        )
        assert cm.moveGroupeMatiereTo(str(gm[2].id), 1) == [
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": str(gm[0].id),
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": str(gm[2].id),
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": str(gm[1].id),
                "nom": "rien",
                "position": 2,
                "nbPages": 0,
            },
        ]

    def test_addGroupeMatieres_preprend(self, fk, cm):
        fk.f_annee(id=2019)
        res = cm.addGroupeMatiere("annee:2019")
        with db_session:
            new = cm.db.GroupeMatiere.select().first()
            assert new.matieres.count() == 1
        assert res == [
            {
                "annee": 2019,
                "bgColor": QColor("white"),
                "fgColor": QColor("black"),
                "id": str(new.id),
                "nom": "nouveau groupe",
                "position": 0,
                "nbPages": 0,
            }
        ]

    def test_addGroupeMatieres(self, fk, cm):
        gm = fk.b_groupeMatiere(
            3, annee=2017, nom="rien", bgColor="red", fgColor="blue"
        )
        res = cm.addGroupeMatiere(str(gm[2].id))
        with db_session:
            new = cm.db.GroupeMatiere.select()[:][-1]
            assert new.matieres.count() == 1

        assert [
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": str(gm[0].id),
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": str(gm[1].id),
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("white"),
                "fgColor": QColor("black"),
                "id": str(new.id),
                "nom": "nouveau",
                "position": 2,
                "nbPages": 0,
            },
            {
                "annee": 2017,
                "bgColor": QColor("red"),
                "fgColor": QColor("blue"),
                "id": str(gm[2].id),
                "nom": "rien",
                "position": 3,
                "nbPages": 0,
            },
        ]
        with db_session:
            assert (
                cm.db.GroupeMatiere[str(new.id)].matieres.select().first().nom
                == "nouvelle matière"
            )

    @pytest.mark.parametrize(
        "nb, res, end_color",
        [
            (0, [], QColor("pink")),
            (
                1,
                [
                    {
                        "activites": [],
                        "bgColor": QColor.fromRgbF(
                            1.000000, 0.000000, 0.000000, 1.000000
                        ),
                        "fgColor": QColor.fromRgbF(
                            0.000000, 0.501961, 0.000000, 1.000000
                        ),
                        "groupe": "bf44711d-1c0f-444a-af48-869f62974696",
                        "id": "xx",
                        "nom": "rien",
                        "position": 0,
                        "nbPages": 0,
                    },
                ],
                QColor("red"),
            ),
            (
                3,
                [
                    {
                        "activites": [],
                        "bgColor": QColor.fromRgbF(
                            1.000000, 0.000000, 0.000000, 1.000000
                        ),
                        "fgColor": QColor.fromRgbF(
                            0.000000, 0.501961, 0.000000, 1.000000
                        ),
                        "groupe": "bf44711d-1c0f-444a-af48-869f62974696",
                        "id": "xx",
                        "nom": "rien",
                        "position": 0,
                        "nbPages": 0,
                    },
                    {
                        "activites": [],
                        "bgColor": QColor.fromRgbF(
                            1.000000, 0.423529, 0.423529, 1.000000
                        ),
                        "fgColor": QColor.fromRgbF(
                            0.000000, 0.501961, 0.000000, 1.000000
                        ),
                        "groupe": "bf44711d-1c0f-444a-af48-869f62974696",
                        "id": "xx",
                        "nom": "rien",
                        "position": 1,
                        "nbPages": 0,
                    },
                    {
                        "activites": [],
                        "bgColor": QColor.fromRgbF(
                            1.000000, 0.847059, 0.847059, 1.000000
                        ),
                        "fgColor": QColor.fromRgbF(
                            0.000000, 0.501961, 0.000000, 1.000000
                        ),
                        "groupe": "bf44711d-1c0f-444a-af48-869f62974696",
                        "id": "xx",
                        "nom": "rien",
                        "position": 2,
                        "nbPages": 0,
                    },
                ],
                QColor("red"),
            ),
        ],
    )
    def test_applyGroupeDegrade_with_color(self, fk, cm, nb, res, end_color):
        gm = fk.f_groupeMatiere(
            id="bf44711d-1c0f-444a-af48-869f62974696", bgColor="pink"
        )
        print(gm.id)
        fk.b_matiere(nb, groupe=str(gm.id), nom="rien", bgColor="blue", fgColor="green")
        pre_res = cm.applyGroupeDegrade(str(gm.id), QColor("red"))
        for mat in pre_res:
            mat["id"] = "xx"

        assert pre_res == res

        with db_session:
            assert cm.db.GroupeMatiere[str(gm.id)].bgColor == end_color

    def test_reApplyGroupeDegrade(self, fk, cm):
        gm = fk.f_groupeMatiere(bgColor="red")
        mats = fk.b_matiere(
            3, groupe=gm.id, nom="rien", bgColor="blue", fgColor="green"
        )
        pre_res = cm.reApplyGroupeDegrade(str(gm.id))
        for mat in pre_res:
            mat["id"] = "xx"
        assert pre_res == [
            {
                "activites": [],
                "bgColor": QColor.fromRgbF(1.000000, 0.000000, 0.000000, 1.000000),
                "fgColor": QColor.fromRgbF(0.000000, 0.501961, 0.000000, 1.000000),
                "groupe": str(gm.id),
                "id": "xx",
                "nom": "rien",
                "position": 0,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor.fromRgbF(1.000000, 0.423529, 0.423529, 1.000000),
                "fgColor": QColor.fromRgbF(0.000000, 0.501961, 0.000000, 1.000000),
                "groupe": str(gm.id),
                "id": "xx",
                "nom": "rien",
                "position": 1,
                "nbPages": 0,
            },
            {
                "activites": [],
                "bgColor": QColor.fromRgbF(1.000000, 0.847059, 0.847059, 1.000000),
                "fgColor": QColor.fromRgbF(0.000000, 0.501961, 0.000000, 1.000000),
                "groupe": str(gm.id),
                "id": "xx",
                "nom": "rien",
                "position": 2,
                "nbPages": 0,
            },
        ]

        with db_session:
            assert cm.db.GroupeMatiere[str(gm.id)].bgColor == QColor("red")

    def test_updateGroupeNom(self, fk, cm):
        gm = fk.f_groupeMatiere(nom="bla")
        cm.updateGroupeMatiereNom(str(gm.id), "meuh")
        with db_session:
            assert cm.db.GroupeMatiere[str(gm.id)].nom == "meuh"
