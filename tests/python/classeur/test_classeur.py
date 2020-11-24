import pytest
from fixtures import check_args
from mycartable.classeur.classeur import Classeur
from pony.orm import db_session


@pytest.fixture()
def cl_data(
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
    gp._page00 = fk.f_page(activite=gp._acts[0][0], td=True)
    gp._page01 = fk.f_page(activite=gp._acts[0][1], td=True)
    gp._page10 = fk.f_page(activite=gp._acts[1][0], td=True)
    return gp


@pytest.fixture()
def classeur(cl_data, ddbr):
    c = Classeur()
    c.db = ddbr
    c.annee = 2019
    return c


def test_check_args():
    check_args(Classeur.setCurrentMatiere, int)
    check_args(Classeur.setCurrentMatiere, str, slot_order=1)


def test_init_base():
    c = Classeur()
    assert c.annee == 0
    assert c.matieresDispatcher is None
    assert c.currentMatiere is None
    assert c.pagesParActivite == []
    assert c.page == None


def test_init_apres_annee(classeur):
    assert classeur.annee == 2019
    assert classeur.matieresDispatcher.annee_active == 2019
    assert classeur.currentMatiere is None
    assert classeur.pagesParActivite == []
    assert classeur.page == None


def test_init_apres_matiere(classeur, cl_data, ddbr):
    matid = cl_data._mats[0]
    classeur.currentMatiere = matid
    assert classeur.annee == 2019
    assert classeur.matieresDispatcher.annee_active == 2019
    assert classeur.currentMatiere.nom == "un"
    assert classeur.currentMatiere.id == matid
    with db_session:
        assert classeur.pagesParActivite == ddbr.Matiere[matid].pages_par_activite()
    assert classeur.page == None


def test_init_apres_page(classeur, cl_data):
    p = cl_data._page00
    classeur.setPage(p["id"])
    assert classeur.currentMatiere.id == p["matiere"]


def test_init_page_apres_autre_matiere_active(classeur, cl_data, qtbot):
    classeur.currentMatiere = cl_data._mats[0]
    with qtbot.waitSignal(classeur.currentMatiereChanged):
        classeur.setPage(cl_data._page10["id"])
    assert classeur.currentMatiere.id == classeur.page.matiereId
    assert classeur.currentMatiere.id == cl_data._mats[1]


def test_init_page_apres_autre_dans_meme_matiere(classeur, cl_data, qtbot):
    classeur.currentMatiere = cl_data._mats[1]
    with qtbot.waitSignal(classeur.currentMatiereChanged):
        classeur.setPage(cl_data._page00["id"])
    with qtbot.assertNotEmitted(classeur.currentMatiereChanged):
        classeur.setPage(cl_data._page01["id"])


def test_setPage_emitted_signals(classeur, cl_data, qtbot):
    with qtbot.waitSignals([classeur.activitesChanged]):
        classeur.setPage(cl_data._page00["id"])


def test_newPage(classeur, cl_data, qtbot):
    classeur.setPage(cl_data._page00["id"])
    assert classeur.page.parent() == classeur
    old = classeur.page
    with qtbot.waitSignal(classeur.pageChanged):
        classeur.newPage(str(cl_data._acts[0][0].id))
    assert classeur.page != old


def test_deletePage(classeur, cl_data, qtbot):
    classeur.setPage(cl_data._page00["id"])
    with qtbot.waitSignal(classeur.pageChanged):
        classeur.deletePage()
    assert classeur.page is None


def test_set_matiere(classeur, cl_data, qtbot):
    # not found
    classeur.currentMatiere = "8bfd9c48-a00c-468d-8fdd-797d3e1718c9"
    assert classeur.currentMatiere is None

    # par id (str)
    matid = cl_data._mats[0]
    classeur.setCurrentMatiere(matid)
    assert classeur.currentMatiere.id == matid

    # par index (int)
    matid = cl_data._mats[1]
    classeur.setCurrentMatiere(1)
    assert classeur.currentMatiere.id == matid

    # same == no change
    with qtbot.assertNotEmitted(classeur.currentMatiereChanged):
        classeur.setCurrentMatiere(1)


def test_connections(qtbot, classeur, cl_data):
    with qtbot.waitSignals([classeur.currentMatiereChanged, classeur.activitesChanged]):
        classeur.setCurrentMatiere(1)
