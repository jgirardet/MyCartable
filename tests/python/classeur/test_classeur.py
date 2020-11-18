import pytest
from fixtures import check_args
from mycartable.classeur.classeur import Classeur
from pony.orm import db_session


@pytest.fixture()
def create_matiere(
    fk,
):
    gp = fk.f_groupeMatiere(annee=2019)

    def activ(mat):
        return (
            fk.f_activite(nom="un", matiere=mat),
            fk.f_activite(nom="deux", matiere=mat),
            fk.f_activite(nom="trois", matiere=mat),
        )

    _mats = []
    a = fk.f_matiere(nom="un", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id)
    _mats.append(str(a.id))
    a = fk.f_matiere(nom="deux", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id)
    _mats.append(str(a.id))
    a = fk.f_matiere(
        nom="trois", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id
    )
    _mats.append(str(a.id))
    a = fk.f_matiere(
        nom="quatre", _fgColor=4294967295, _bgColor=4294901760, groupe=gp.id
    )
    _mats.append(str(a.id))
    gp._mats = _mats
    gp._acts = []
    for m in gp._mats:
        gp._acts.append(activ(m))
    # breakpoint()
    gp._page = fk.f_page(activite=gp._acts[0][0], td=True)
    return gp


@pytest.fixture()
def classeur(create_matiere, ddbr):
    c = Classeur()
    c.db = ddbr
    c.annee = 2019
    return c


class TestClasseur:
    def test_check_args(self):
        check_args(Classeur.setCurrentMatiere, int)
        check_args(Classeur.setCurrentMatiere, str, slot_order=1)

    def test_init_base(self):
        c = Classeur()
        assert c.annee == 0
        assert c.matieresDispatcher is None
        assert c.currentMatiere is None
        assert c.pagesParActivite == []

    def test_init_apres_annee(self, classeur):
        assert classeur.annee == 2019
        assert classeur.matieresDispatcher.annee_active == 2019
        assert classeur.currentMatiere is None
        assert classeur.pagesParActivite == []

    def test_init_apres_matiere(self, classeur, create_matiere, ddbr):
        matid = create_matiere._mats[0]
        classeur.currentMatiere = matid
        assert classeur.annee == 2019
        assert classeur.matieresDispatcher.annee_active == 2019
        assert classeur.currentMatiere.nom == "un"
        assert classeur.currentMatiere.id == matid
        print(matid)
        with db_session:
            assert classeur.pagesParActivite == ddbr.Matiere[matid].pages_par_activite()

    def test_set_matiere(self, classeur, create_matiere, qtbot):
        # not found
        classeur.currentMatiere = "8bfd9c48-a00c-468d-8fdd-797d3e1718c9"
        assert classeur.currentMatiere is None

        # par id (str)
        matid = create_matiere._mats[0]
        classeur.setCurrentMatiere(matid)
        assert classeur.currentMatiere.id == matid

        # par index (int)
        matid = create_matiere._mats[1]
        classeur.setCurrentMatiere(1)
        assert classeur.currentMatiere.id == matid

        # same == no change
        with qtbot.assertNotEmitted(classeur.currentMatiereChanged):
            classeur.setCurrentMatiere(1)

    def test_connections(self, qtbot, classeur, create_matiere):
        with qtbot.waitSignals(
            [classeur.currentMatiereChanged, classeur.activitesChanged]
        ):
            classeur.setCurrentMatiere(1)
