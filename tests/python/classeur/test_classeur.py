from datetime import datetime
from uuid import UUID

import pytest
from PyQt5.QtWidgets import QUndoCommand
from tests.python.fixtures import check_args, disable_log
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
    gp._page00 = fk.f_page(
        activite=gp._acts[0][0], td=True, created=datetime(2019, 12, 31)
    )
    gp._page01 = fk.f_page(
        activite=gp._acts[0][1], td=True, created=datetime(2019, 12, 10)
    )
    gp._page10 = fk.f_page(
        activite=gp._acts[1][0], td=True, created=datetime(2019, 12, 1)
    )
    return gp


@pytest.fixture()
def classeur(cl_data, ddbr):
    c = Classeur()
    c.db = ddbr
    with disable_log():
        c.annee = 2019
    return c


def test_init_base():
    c = Classeur()
    assert c.annee == 0
    assert c.matieresDispatcher is None
    assert c.currentMatiere is None
    assert c.recents == None
    assert c.page == None


def test_anne_set(qtbot, classeur):
    with qtbot.assertNotEmitted(classeur.anneeChanged):
        # with disable_log():
        classeur.annee = 0
    assert classeur.matieresDispatcher is None
    assert classeur.currentMatiere is None
    assert classeur.recents == None
    assert classeur.page == None


def test_init_apres_annee(classeur, fk):
    assert classeur.annee == 2019
    assert classeur.matieresDispatcher.annee_active == 2019
    assert classeur.currentMatiere is None
    assert classeur.recents.rowCount() == 3
    assert classeur.page == None


def test_init_apres_matiere(classeur, cl_data, ddbr):
    matid = cl_data._mats[0]
    classeur.currentMatiere = matid
    assert classeur.annee == 2019
    assert classeur.matieresDispatcher.annee_active == 2019
    assert classeur.currentMatiere.nom == "un"
    assert classeur.currentMatiere.id == matid
    assert classeur.recents.rowCount() == 3
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


def test_newPage(classeur, cl_data, qtbot):
    classeur.setPage(cl_data._page00["id"])
    assert classeur.page.parent() == classeur
    old = classeur.page
    with qtbot.waitSignals(
        [
            classeur.pageChanged,
            classeur.recents.rowsInserted,
            classeur.currentMatiere.activites[0].pages.rowsInserted,
        ]
    ):
        classeur.newPage(str(cl_data._acts[0][0].id))
    assert classeur.page != old


def test_deletePage(classeur, cl_data, qtbot):
    classeur.setPage(cl_data._page00["id"])
    with qtbot.waitSignals(
        [
            classeur.pageChanged,
            classeur.recents.rowsRemoved,
            classeur.currentMatiere.activites[0].pages.rowsRemoved,
        ]
    ):
        classeur.deletePage()
    assert classeur.page is None


def test_set_matiere(classeur, cl_data, qtbot):
    # not found
    with disable_log():
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

    # par UUID
    matid = cl_data._mats[1]
    classeur.setCurrentMatiere(UUID(matid))
    assert classeur.currentMatiere.id == matid

    # same == no change
    with qtbot.assertNotEmitted(classeur.currentMatiereChanged):
        classeur.setCurrentMatiere(1)


def test_connections(qtbot, classeur, cl_data):
    with qtbot.waitSignals([classeur.currentMatiereChanged]):
        classeur.setCurrentMatiere(1)


def test_currentMatiere_index(classeur, qtbot, cl_data):
    assert classeur.currentMatiereIndex == 0
    classeur.setCurrentMatiere(1)
    assert classeur.currentMatiereIndex == 1
    assert classeur.currentMatiere.id == cl_data._mats[1]


def test_recents(classeur, ddbr, fk, qtbot):
    with db_session:
        assert ddbr.Page.recents(classeur.annee) == classeur.recents._data
        assert classeur.recents.rowCount() == 3

    fk.f_annee(2099)
    with qtbot.waitSignal(classeur.recentsChanged):
        classeur.annee = 2099


def test_page_titre_changed(classeur, cl_data, qtbot):
    classeur.setPage(cl_data._page00["id"])
    with qtbot.waitSignal(classeur.recents.dataChanged):
        classeur.page.titre = "hello !!!"
    r = classeur.recents
    assert r.data(r.index(0, 0), r.TitreRole) == "hello !!!"
    ac = classeur.currentMatiere.activites[0]
    assert ac.pages.data(r.index(0, 0), r.TitreRole) == "hello !!!"


def test_movePage(classeur, cl_data, fk, qtbot):
    r = classeur.recents
    classeur.setPage(cl_data._page00["id"])
    ac0 = classeur.currentMatiere.activites[0]
    ac1 = classeur.currentMatiere.activites[1]
    new_ac = cl_data._acts[1][0]
    with qtbot.waitSignals([r.modelReset, ac0.pages.modelReset, ac1.pages.modelReset]):
        classeur.movePage(cl_data._page00["id"], new_ac.id)

    with db_session:
        item = fk.db.Page[cl_data._page00["id"]]
        assert item.activite.id == new_ac.id


def test_pageModified_move_on_top_of_recents(classeur, cl_data, fk, qtbot):
    r = classeur.recents
    classeur.setPage(cl_data._page10["id"])
    with qtbot.waitSignal(r.rowsMoved):
        classeur.page.update_modified_if_viewed()

    assert r._data[0]["id"] == cl_data._page10["id"]


def test_undoStack(classeur):
    class Com(QUndoCommand):
        def redo(self) -> None:
            classeur.aaa = "aaa"

    classeur.undoStack.push(Com())
    assert classeur.aaa == "aaa"
